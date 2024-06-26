import chromadb
from chromadb.utils import embedding_functions

chroma_client = chromadb.Client()

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-mpnet-base-v2',
)

collection = chroma_client.create_collection(
    name='properties',
    embedding_function=embedding_function,
)

collection.add(
    documents=[
        'Property with bike lanes near rail.',
        'Car dependant sprawl next to a supermarket.',
    ],
    metadatas=[
        { 'source': 'goggle', 'page': 1 },
        { 'source': 'bong' },
    ],
    ids=[
        'id1',
        'id2'
    ]
)

search_terms = [
    'bikes',
    'very cool',
    'disconnected',
    'shit',
]

for term in search_terms:
    print(f'Searching for term: "{term}"')
    results = collection.query(
        query_texts=[term],
        n_results=1,
        # include=['distances', 'metadata', 'documents'],
    )

    print(results)
