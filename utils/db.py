'''Provides the database interface.'''
import sys
import os
from typing import List

import chromadb

from chromadb.utils import embedding_functions
from uuid import uuid4 as uuid

from config import DB_SAVE_NAME

os.path.dirname(sys.executable)

class ChromaDb():
	def __init__(self) -> None:
		self.client = None
		self.collection = None
		self.collection_name = None
		self.embedding_function = None

	def create_client(self):
		self.client = chromadb.PersistentClient(path=DB_SAVE_NAME)

	def create_collection(self, collection_name: str):
		self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
			model_name='all-mpnet-base-v2',
		)
		self.collection_name = collection_name
		self.collection = self.client.get_or_create_collection(
			name='properties',
			embedding_function=self.embedding_function,
		)
		return self.collection
	
	def get_client(self):
		return self.client
	
	def get_collection(self):
		return self.collection

	def add_document(self, content: str, meta_data: dict, row_id: str):
		self.collection.add(
			documents=[content],
			metadatas=[meta_data],
			ids=[row_id],
		)

	def add_many_documents(self, content_array: List[str]):
		documents = []
		metadatas = []
		ids = []

		for row in content_array:
			documents.append(row)
			metadatas.append({ 'source': 'standard' })
			ids.append(str(uuid()))

		self.collection.add(
			documents=documents,
			metadatas=metadatas,
			ids=ids,
		)

	def search(
		self,
		search_term: str,
		n_results: int=1,
		include: List[str]=['documents'],
	):
		result = self.collection.query(
			query_texts=[search_term],
			n_results=n_results,
			include=include,
		)
		return result

db = ChromaDb()
