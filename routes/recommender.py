import openai

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from config import SYSTEM_PROMPT

from utils.db import db

router = APIRouter()


class RecommenderRequest(BaseModel):
	'''Request model for the agent recommender route.'''
	transport: str
	community: str
	size: str
	amenities: str


@router.post('/')
def get_recommendations(preferences: RecommenderRequest):
	'''Main endpoint for the agent. Provides RAG responses for the listing database.'''
	logger.debug(preferences)
	query_str = f'{preferences.transport} {preferences.size} {preferences.community} {preferences.amenities}'
	result = db.search(search_term=query_str)

	prompt = f'''
You will be provided a set of USER PREFERENCES for a property and also a PROPERTY LISTING, chosen from our recommendation system.
Please write a description for the listing, tailored to the specific USER PREFERENCES.
Please enhance and enrich key points within the description, without inventing or hallucinating any new information.

USER PREFERENCES:
Transport & Connectivity: {preferences.transport}
Size, bedroom and bathroom count, any other features: {preferences.size}
Community: {preferences.community}
Amenities: {preferences.amenities}

PROPERTY LISTING:
{result['documents'][0][0]}
	'''

	try:
		llm_response = openai.ChatCompletion.create(
			model='gpt-3.5-turbo',
			messages=[
				{ 'role': 'system', 'content': SYSTEM_PROMPT },
				{ 'role': 'user', 'content': prompt },
			],
			# temperature=1,
			# max_tokens=256,
			# top_p=1,
			# frequency_penalty=0,
			# presence_penalty=0,
		)

		return {
			'response': llm_response.choices[0].message.content,
			'rawListing': result['documents'][0][0]
		}
	except Exception as e:
		return str(e)


