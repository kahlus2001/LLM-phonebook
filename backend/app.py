import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from phonebook_agent import agent
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route('/api/llm/contacts', methods=['POST'])
def llm_contacts():
    data = request.get_json()
    command = data.get('command')
    if not command:
        return jsonify({'message': 'No command provided', 'contacts': []}), 400

    try:
        response = agent.invoke(command)
        # If agent returns a dict with 'output', unwrap it
        if isinstance(response, dict) and 'output' in response:
            response = response['output']
        # If agent returns not a dict, wrap it
        if not isinstance(response, dict) or 'message' not in response or 'contacts' not in response:
            return jsonify({"message": str(response), "contacts": []})
        return jsonify(response)
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'contacts': []}), 500



if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'), 
        port=os.getenv('PORT', 5001), 
        debug=True
    )
