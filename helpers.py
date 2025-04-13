import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API")
PINECONE_API_KEY = os.getenv("PINECONE_API")

client = OpenAI(api_key=OPENAI_API_KEY)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(host = 'gghackathonv2-kdd7hth.svc.aped-4627-b74a.pinecone.io')

def embed(query):
    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding
    return query_embedding

def context(query_embedding, top_k = 3):
    results = index.query(
    vector=query_embedding,
    top_k=top_k,
    include_metadata=True
    )

    contexts = [match['metadata']['text'] for match in results['matches']]
    return "\n".join(contexts)

def chat(query, context):
    system_prompt = """
        You are an intelligent legal assistant for public defenders. 
        Your job is to analyze a client's situation and recommend the most effective legal defense strategies by drawing on patterns from prior similar legal cases.
        Be specific, strategic, and cite similarities or trends from the provided case context.
        If the data suggests racial or gender-based disparities, highlight them to inform a fair defense.
            """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""
    Client Situation:
    {query}

    Relevant Past Cases:
    {context}

    Based on the above, what is the most effective defense strategy and what outcome is most likely? Please provide a concise, well-reasoned answer supported by case data.
                    """
                }
            ],
            max_tokens=600
        )

    return response.choices[0].message.content.strip()