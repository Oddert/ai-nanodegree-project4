import pandas as pd
import lancedb
import tiktoken

# Sample data
data = {
    'description': [
        'This is the first document.',
        'Here is the second document.',
        'This is another document.',
        'Yet another example document.'
    ]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Tokenizer function
tokeniser = tiktoken.get_encoding('cl100k_base')

# Encode the descriptions into vectors
df['vector'] = [tokeniser.encode(x) for x in df['description']]

# Connect to LanceDB
db = lancedb.connect('./lancedb_example')

# Create a LanceDB table
db.create_table('example_table', df, exist_ok=True, on_bad_vectors='drop')

# Open the table
table = db.open_table('example_table')

# Print the table schema and data
print("Schema:", table.schema)
print("Data:")
for record in table.to_pandas().itertuples():
    print(record)

# Define a function to convert text to vector
def text_to_vector(text):
    return tokeniser.encode(text)

# Example query: Find documents similar to a given text
query_text = 'example document'
query_vector = text_to_vector(query_text)

# Perform the query (assuming LanceDB has a `query` method that accepts vectors)
results = table.search(query_vector).limit(1)

# Print the query results
print("\nQuery results for:", query_text)
print(results.to_list())
# for result in results:
#     print(result)
