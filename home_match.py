
'''Entry point for the application.'''
# pylint: disable=broad-exception-caught
import os

import uvicorn

import pandas as pd
import openai

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import (
	LISTINGS_RAW_FILENAME,
	openai_api_key,
	port,
)

from routes.recommender import router as recommender

openai.api_key = openai_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=unused-argument
	'''Initialises the db instance.'''
	df = pd.read_csv(f'./{LISTINGS_RAW_FILENAME}')
	os.environ['OPENAI_API_KEY'] = openai_api_key
	print(df)
	yield

server = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory='templates')


@server.get('/', response_class=HTMLResponse)
def home(request: Request):
	'''Renders the agent front end.'''
	return templates.TemplateResponse(
		# request=request,
		name='agent.html',
		context={
			'request': request,
		},
	)


server.include_router(recommender, prefix='/recommender', tags=['api'])

server.mount('/static', StaticFiles(directory='static'), name='static')

if __name__ == '__main__':
	uvicorn.run(
		'home_match:server',
		host='127.0.0.1',
		port=int(port),
		reload=True,
	)
