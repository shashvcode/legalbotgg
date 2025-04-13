import os
from openai import OpenAI
from pinecone import Pinecone

# Load your API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Test OpenAI API Key
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("OpenAI API Key is valid. Response:", response)
except Exception as e:
    print("OpenAI Error:", str(e))

# Test Pinecone API Key
try:
    pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
    index = pinecone_client.Index("your_index_name")  # Replace with your actual index name
    print("Pinecone API Key is valid. Index accessed successfully.")
except Exception as e:
    print("Pinecone Error:", str(e))