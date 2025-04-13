from flask import Flask, request, jsonify
from flask_cors import CORS
from helpers import embed, context, chat
from dotenv import load_dotenv
import logging
import traceback
import os
import sys

# Configure logging to show more details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, 
     origins=["http://localhost:5176"],  # Explicitly allow your frontend origin
     allow_headers=["Content-Type"],
     supports_credentials=True)

@app.route("/legalchat", methods=["POST", "OPTIONS"])
def legal_chat():
    if request.method == "OPTIONS":
        # Needed for CORS preflight
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5176")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response
        
    logger.debug("Received request at /legalchat")
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        
        query = data.get("query")
        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Print environment variables for debugging
        logger.debug(f"OPENAI_API_KEY set: {'OPENAI_API_KEY' in os.environ}")
        logger.debug(f"PINECONE_API_KEY set: {'PINECONE_API_KEY' in os.environ}")

        logger.debug("Generating embedding...")
        try:
            embedded = embed(query)
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Error generating embedding", "details": str(e)}), 500
        
        logger.debug("Getting context...")
        try:
            legal_context = context(embedded, top_k=5)
        except Exception as e:
            logger.error(f"Context error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Error getting context", "details": str(e)}), 500
        
        logger.debug("Generating chat response...")
        try:
            answer = chat(query, legal_context)
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Error generating chat response", "details": str(e)}), 500
        
        response = jsonify({"answer": answer})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5176")
        return response, 200
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    # Check if environment variables are set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY is not set in environment variables")
        sys.exit(1)
    if not os.getenv("PINECONE_API_KEY"):
        logger.error("PINECONE_API_KEY is not set in environment variables")
        sys.exit(1)
        
    logger.info("Starting Flask server on port 5002")
    app.run(debug=True, port=5002)