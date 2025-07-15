from flask import Flask, jsonify, request as f_request
from external import Mistral_Ai
from dotenv import load_dotenv
import os
import json

load_dotenv()

mistral_agent = Mistral_Ai(os.getenv("MISTRAL_KEY"))
app = Flask(__name__)

@app.route('/', methods=['POST'])
def mock_api():
    request_data = f_request.get_json()

    print("--- Received POST request ---")
    print(f"Client IP: {f_request.remote_addr}")
    print(f"Headers: {f_request.headers}")
    print(f"JSON Payload:\n{json.dumps(request_data, indent=2)}")

    if 'messages' in request_data and isinstance(request_data['messages'], list):
        messages_lis = request_data['messages']
        print(f"*** CAPTURED PROMPTS: {messages_lis} ***")
        messages_lis

    return jsonify(mistral_agent.generate_text(messages_lis)), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)