import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, PineconeException

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Pinecone client
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("gghackathonv2")
except Exception as e:
    logger.error(f"Error initializing Pinecone: {str(e)}")
    raise

def embed(query):
    try:
        logger.debug(f"Generating embedding for query: {query}")
        query_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding
        return query_embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise

def context(query_embedding, top_k = 3):
    try:
        logger.debug(f"Querying Pinecone with top_k={top_k}")
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        if not results.get('matches'):
            logger.warning("No matches found in Pinecone")
            return "No relevant cases found."

        contexts = [match['metadata']['text'] for match in results['matches']]
        return "\n".join(contexts)
    except Exception as e:
        logger.error(f"Error getting context from Pinecone: {str(e)}")
        raise

def chat(query, context):
    try:
        system_prompt = """
            You are an intelligent legal assistant for public defenders. 
            Your job is to analyze a client's situation and recommend the most effective legal defense strategies by drawing on patterns from prior similar legal cases.
            Be specific, strategic, and cite similarities or trends from the provided case context.
            If the data suggests racial or gender-based disparities, highlight them to inform a fair defense.
                """

        logger.debug("Sending request to OpenAI")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""Client Situation: {query}
Relevant Past Cases: {context}
Based on the above, what is the most effective defense strategy and what outcome is most likely? Please provide a concise, well-reasoned answer supported by case data."""
                }
            ],
            max_tokens=600
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise