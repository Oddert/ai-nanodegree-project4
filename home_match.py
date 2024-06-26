#A starter file for the HomeMatch application if you want to build your solution in a Python program instead of a notebook. 

import uvicorn

from langchain.llms import OpenAI

import lancedb
import tiktoken
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import AutoTokenizer

from config import TABLE_NAME, LISTINGS_RAW_FILENAME

from routes.home import router as home

# tokeniser = tiktoken.get_encoding('cl100k_base')
tokeniser = AutoTokenizer.from_pretrained('gpt2')
tokeniser.add_special_tokens({'pad_token': '[PAD]'})

@asynccontextmanager
async def lifespan(app: FastAPI):
	print('[load db]')
	# load db
	df = pd.read_csv(f'./{LISTINGS_RAW_FILENAME}')
	# tokeniser = tiktoken.get_encoding('cl100k_base')

	# Ensure all vectors are lists of integers - thank you ChatGPT...
	df['vector'] = [list(map(int, tokeniser.encode(x, padding='max_length'))) for x in df['description']]
	print('[df defined]')
	db = lancedb.connect('./lancedb')

	try:
		db.drop_table(TABLE_NAME)
	except:
		print('table doesn\'t exist')

	db.create_table(TABLE_NAME, df, exist_ok=True, on_bad_vectors='drop')
	print('[table created]')
	table = db.open_table(TABLE_NAME)
	print(table.search(tokeniser.encode('bike', padding='max_length')).limit(1))
	print('[finished]')
	yield
	# db.close()
	# close db connection

# @asynccontextmanager
# async def lifespan(app: FastAPI):
# 	# load db
# 	df = pd.read_csv(f'./{LISTINGS_RAW_FILENAME}')
# 	tokeniser = tiktoken.get_encoding('cl100k_base')
# 	# tokeniser = AutoTokenizer.from_pretrained('distilbert-base-uncased')
# 	df['vector'] = [tokeniser.encode(x) for x in df['description']]
# 	print(df)
# 	db = lancedb.connect('./lancedb')
# 	# db.drop_table(TABLE_NAME, )
# 	db.create_table(TABLE_NAME, df, exist_ok=True, on_bad_vectors='fill')
# 	table = db.open_table(TABLE_NAME)
# 	print(table.search(tokeniser.encode('bike lanes')).limit(1))
# 	yield
# 	db.close()
# 	# close db connection

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
def one(request: Request):
	return templates.TemplateResponse(
		# request=request,
		name='agent.html',
		context={
			'request': request,
		},
	)

@app.get('/s', response_class=HTMLResponse)
def one(request: Request):
	db = lancedb.connect('./lancedb')
	table = db.open_table(TABLE_NAME)
	# query = table.search('bike lanes').limit(1).to_list()
	query = table.search(tokeniser.encode('bike lanes', padding='max_length')).limit(1).to_list()
	return str(query)

app.include_router(home, tags=['home'])

app.mount('/static', StaticFiles(directory='static'), name='static')

if __name__ == '__main__':
	uvicorn.run(
		'home_match:app',
		host='127.0.0.1',
		port=8001,
		reload=True,
	)
