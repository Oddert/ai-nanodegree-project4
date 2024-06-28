import configparser

config = configparser.ConfigParser()
config.read('envfile.ini', encoding='utf-8')
config_default = config['DEFAULT']

openai_api_key = config_default['OPENAI_API_KEY']
port = config_default['PORT'] if 'PORT' in config_default else '8001'

TABLE_NAME = 'listings'
LISTINGS_RAW_FILENAME = 'generated-listings.csv'
DB_SAVE_NAME = 'listings-db'
SYSTEM_PROMPT = '''You are a helpful and cheerful real estate bot dedicated to finding the perfect property for your users. You are clear, articulate and enthusiastic but also professional and mature. You articulate clear benefits of the chosen properties and do not shy away from any downsides or aspects of the listing that contradict the user preferences. You make good use of line breaks and paragraphs, making sure to structure your responses in a clear, hierarchical format.'''

questions = [
	{
		'message': 'What are you\'re transport priorities? What connections would you need and how would you be looking to get around?',
		'variableKey': 'transport',
	},
	{
		'message': 'What size of a property would you be looking for? How many bedrooms and bathrooms? Any other must-haves?',
		'variableKey': 'size',
	},
	{
		'message': 'How would you describe the community and local scene in your perfect world?',
		'variableKey': 'community',
	},
	{
		'message': 'Are there any amenities or local features that you\'d need near by?',
		'variableKey': 'amenities',
	},
]
