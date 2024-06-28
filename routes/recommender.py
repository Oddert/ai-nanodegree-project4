import openai
# import pandas as pd

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain_core.prompts import PromptTemplate
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
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

from utils.db import db

router = APIRouter()


prompt_template = '''
The following is a friendly conversation between a human and an AI. The AI is enthusiastic yet professional and does its best to answer questions with close attention paid to the user-provided context.
The AI's job is to act as a real estate agent, finding listings tailored to the user's preferences by highlighting key features for the user.
The AI must enhance specific features relating to the user's preferences, without inventing or hallucinating any new details.
If these instructions are not met, the user will not be able to understand the AI's output.

Summary of conversation:
{history}

Current conversation:
{chat_history_lines}

Human: {input}
AI:'''

def get_plot_rating_instructions(db, question: str):
	return f"""
        =====================================
    === START HOME MATCH FOR {question} ===
    THe below found documents which is similar to the user preference.
    {db.similarity_search(question, k=3)}
    === END HOME MATCH SUMMARY ===
    =====================================

    RATING INSTRUCTIONS THAT MUST BE STRICTLY FOLLOWED:
    AI will provide a highly personalized Home Recommendation based only on the buyer preferences summary human provided
    and human answers to questions included with the context.
    AI should be very sensible to human personal preferences captured in the answers to personal questions,
    and should not be influenced by anything else.
    AI will also build a persona for human based on human answers to questions, and use this persona to rate the home match.

    OUTPUT FORMAT:
    First, include that persona you came up with in the home recommendation. Describe the persona in a few sentences.
    Explain how human preferences captured in the answers to personal questions influenced creation of this persona.
    In addition, consider other similar features of home for this human that you might have as they might give you more information about human's preferences.
    Your goal is to provide a home match recommendation that is as close as possible to the buyer preferences.
    Remember that human buys home only few times in lifetime and wants to have their perfect home, so your recommendation should be as accurate as possible.
    You will include a logical explanation for your recommendation based on human persona you've build and human responses to questions.
    YOUR REVIEW MUST END WITH TEXT: Thank you for your Query
    FOLLOW THE INSTRUCTIONS STRICTLY, OTHERWISE HUMAN WILL NOT BE ABLE TO UNDERSTAND YOUR RECOMMENDATION.
"""


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

	prompt = PromptTemplate(
		input_variables=['history', 'input', 'chat_history_lines'],
		template=prompt_template,
	)

	# TODO: write
	# question = 'I would like a property that is'

	# search = new_db.similarity_search(question, k=3)
	summary_memory = ConversationSummaryMemory(
		buffer=f'The human answered {len(questions)} questions based on their preferences. Create a recommendation based on the preferences and found listing.',
		input_key='input',
		llm=model,
		memory_key='agent_summary_memory',
		return_messages=True,
	)

	history = ChatMessageHistory()

	running_memory = ConversationBufferMemory(
		chat_memory=history,
		input_key='input',
		memory_key='agent_buffer_memory',
	)

	memory = CombinedMemory(memories=[running_memory, summary_memory])

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
		history.add_ai_message(user_responses[question['variableKey']])

	history.add_ai_message('Thank you, not please tell me a summary of the property you\'re considering and I can find a recommendation.')

	conversation = ConversationChain(
		llm=model,
		verbose=True,
		memory=memory,
		prompt=prompt,
	)

	return conversation.predict(
		input=get_plot_rating_instructions(new_db, question)
	)

	# try:
	# 	llm_response = openai.ChatCompletion.create(
	# 		model=model_name,
	# 		messages=[
	# 			{ 'role': 'system', 'content': SYSTEM_PROMPT },
	# 			{ 'role': 'user', 'content': prompt },
	# 		],
	# 		# temperature=1,
	# 		# max_tokens=256,
	# 		# top_p=1,
	# 		# frequency_penalty=0,
	# 		# presence_penalty=0,
	# 	)

	# 	return {
	# 		'response': llm_response.choices[0].message.content,
	# 		'rawListing': result['documents'][0][0]
	# 	}
	# except Exception as e:
	# 	return str(e)


