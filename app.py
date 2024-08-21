from flask import Flask, request, jsonify
import os
import anthropic

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/hello')
def hello_world():
    return "Hello, World!"

@app.route('/ask', methods=['GET'])
def ask_claude():
    question = request.args.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return jsonify({"answer": response.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)