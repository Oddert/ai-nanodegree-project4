'''Entry point for the application.'''
import uvicorn

# from langchain.llms import OpenAI

# import lancedb
# import tiktoken
import pandas as pd
# import pyarrow as pa
# import pyarrow.parquet as pq

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
# from transformers import AutoTokenizer

from config import (
	TABLE_NAME,
	LISTINGS_RAW_FILENAME,
)

from utils.db import db

from routes.home import router as home

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
	location: str
	size: str

@server.post('/recommender')
def get_recommendations(preferences: RecommenderRequest):
	'''Main endpoint for the agent. Provides RAG responses for the listing database.'''
	print(preferences)
	# db = lancedb.connect('./lancedb')
	# table = db.open_table(TABLE_NAME)
	query_str = f'{preferences.transport} {preferences.size} {preferences.location}'
	# query = table.search(tokeniser.encode(query_str, padding='max_length')).limit(1).to_list()
	result = db.search(search_term=query_str)
	return result

server.include_router(home, tags=['home'])

server.mount('/static', StaticFiles(directory='static'), name='static')

if __name__ == '__main__':
	uvicorn.run(
		'home_match:server',
		host='127.0.0.1',
		port=8001,
		reload=True,
	)
