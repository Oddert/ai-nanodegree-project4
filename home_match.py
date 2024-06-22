#A starter file for the HomeMatch application if you want to build your solution in a Python program instead of a notebook. 

import uvicorn

from langchain.llms import OpenAI

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes.home import router as home

app = FastAPI()

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

app.include_router(home, tags=['home'])

app.mount('/static', StaticFiles(directory='static'), name='static')

if __name__ == '__main__':
	uvicorn.run(
		'home_match:app',
		host='127.0.0.1',
		port=8001,
		reload=True,
	)
