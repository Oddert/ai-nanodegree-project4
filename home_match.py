'''Entry point for the application.'''
# pylint: disable=broad-exception-caught
import uvicorn

import pandas as pd
import openai

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel
# from transformers import AutoTokenizer

from config import (
	TABLE_NAME,
	LISTINGS_RAW_FILENAME,
	SYSTEM_PROMPT,
	openai_api_key,
)

from utils.db import db

from routes.home import router as home

openai.api_key = openai_api_key

# # tokeniser = tiktoken.get_encoding('cl100k_base')
# tokeniser = AutoTokenizer.from_pretrained('gpt2')
# tokeniser.add_special_tokens({'pad_token': '[PAD]'})

@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=unused-argument
	'''Initialises the db instance.'''
	df = pd.read_csv(f'./{LISTINGS_RAW_FILENAME}')
	print(df)
	db.create_client()
	db.create_collection(TABLE_NAME)
	db.add_many_documents(df['description'])
	yield
	# db.close()
	# close db connection

server = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory='templates')

@server.get('/', response_class=HTMLResponse)
def one(request: Request):
	'''Renders the agent front end.'''
	return templates.TemplateResponse(
		# request=request,
		name='agent.html',
		context={
			'request': request,
		},
	)

class RecommenderRequest(BaseModel):
	'''Request model for the agent recommender route.'''
	transport: str
	community: str
	size: str
	amenities: str


@server.post('/recommender')
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

		return llm_response.choices[0].message.content
	except Exception as e:
		return str(e)

server.include_router(home, tags=['home'])

server.mount('/static', StaticFiles(directory='static'), name='static')

if __name__ == '__main__':
	uvicorn.run(
		'home_match:server',
		host='127.0.0.1',
		port=8001,
		reload=True,
	)
