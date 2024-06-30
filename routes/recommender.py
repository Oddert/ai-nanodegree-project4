'''Handles interactions with the LLM.'''

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.memory import (
	CombinedMemory,
	ConversationBufferMemory,
	ConversationSummaryMemory,
	ChatMessageHistory,
)
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from config import (
	LISTINGS_RAW_FILENAME,
	questions,
	SYSTEM_PROMPT,
)

router = APIRouter()

prompt_template = '''
The following is a friendly conversation between a human and an AI. The AI is enthusiastic yet professional and does its best to answer questions with close attention paid to the user-provided context.
The AI's job is to act as a real estate agent, finding listings tailored to the user's preferences by highlighting key features for the user without inventing any new information.

Summary of conversation:
{conversation_summary}

Current conversation:
{agent_buffer_memory}

Human: {input}
AI:'''


def get_plot_rating_instructions(listing: str):
	'''Creates the initiator prompt.'''
	return '''The user has now provided their preferences and a relevant listing has been found.
The AI system will now respond with a summary description of the listing, highlighting features relevant to the user's preferences.
The AI will not invent new details, hallucinate, or mislead the user.
The AI will be given a response format to for the outline of a response to the user.
Begin the response by addressing the user directly. End the response with "I hope you like this recommendation! Please feel free to search again."

RECOMMENDED PROPERTY LISTING: "{listing}"

DETAILS TO INCLUDE IN THE RESPONSE:
	1) Describe and summarise the listing you have found from the user's preferences.
	2) List key features matching with the user preferences.
	3) Mention details such as:
		a. The number of bedrooms and bathrooms.
		b. Transport options and infrastructure.
		c. Location characteristics, nearby amenities.
		d. Price.

IMPORTANT: If these instructions are not followed, the user will not be able to understand the AI's response.
'''


class RecommenderRequest(BaseModel):
	'''Request model for the agent recommender route.'''
	transport: str
	community: str
	size: str
	amenities: str


@router.get('/questions')
def get_questions():
	'''Returns the schema for the pre-defined questions.'''
	return questions

@router.post('/')
def get_recommendations(preferences: RecommenderRequest):
	'''Main endpoint for the agent. Provides RAG responses for the listing database.'''
	logger.debug(preferences)

	model_name = 'gpt-3.5-turbo'
	temperature = 0
	max_tokens = 1000

	raw_listings = TextLoader(file_path=f'./{LISTINGS_RAW_FILENAME}')
	
	model = ChatOpenAI(
		model_name=model_name,
		temperature=temperature,
		max_tokens=max_tokens
	)

	openai_embedding = OpenAIEmbeddings()

	split = CharacterTextSplitter(
		chunk_size=700,
		chunk_overlap=150,
	)

	docs = split.split_documents(raw_listings.load())

	new_db = Chroma.from_documents(docs, openai_embedding)
	
	query_str = f'{preferences.transport} {preferences.size} {preferences.community} {preferences.amenities}'

	prompt = PromptTemplate(
		input_variables=['conversation_summary', 'input', 'agent_buffer_memory'],
		template=prompt_template,
	)

	history = ChatMessageHistory()

	logger.debug(prompt)

	history.add_user_message(
		'You are and AI assistant that will recommend properties base on my preferences: '
	)

	user_responses = {
		'transport': preferences.transport,
		'community': preferences.community,
		'size': preferences.size,
		'amenities': preferences.amenities,
	}

	for question in questions:
		history.add_ai_message(question['message'])
		history.add_user_message(user_responses[question['variableKey']])

	history.add_ai_message('Thank you, not please tell me a summary of the property you\'re considering and I can find a recommendation.')

	summary_memory = ConversationSummaryMemory(
		buffer=f'The human answered {len(questions)} questions based on their preferences. Create a recommendation based on the preferences and found listing.',
		input_key='input',
		llm=model,
		memory_key='conversation_summary',
		return_messages=True,
	)

	class TempBufferClass(ConversationBufferMemory):
		def save_context(self, inputs, outputs):
			input_str, output_str = self._get_input_output(inputs, outputs)
			self.chat_memory.add_ai_message(output_str)

	running_memory = TempBufferClass(
		chat_memory=history,
		input_key='input',
		memory_key='agent_buffer_memory',
	)

	memory = CombinedMemory(memories=[running_memory, summary_memory])

	conversation = ConversationChain(
		llm=model,
		memory=memory,
		prompt=prompt,
		verbose=True,
	)

	found_documents = new_db.similarity_search(query_str)

	logger.debug(found_documents)

	chosen_document = found_documents[0].page_content

	llm_response = conversation.predict(
		input=get_plot_rating_instructions(chosen_document)
	)

	return {
		'response': llm_response.replace('RECOMMENDED PROPERTY LISTING:', ''),
		'rawListing': chosen_document,
	}
