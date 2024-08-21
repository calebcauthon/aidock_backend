# Flask Claude API Server

This is a simple Flask server that provides two routes:
1. A "Hello, World!" endpoint
2. An endpoint to ask questions to Claude AI

## Setup

1. Install the required packages:
   ```
   pip install flask anthropic
   ```

2. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

3. Run the server:
   ```
   python app.py
   ```

The server will start on `http://127.0.0.1:5000/`.

## Usage

1. Hello World endpoint:
   - URL: `http://127.0.0.1:5000/hello`
   - Method: GET

2. Ask Claude endpoint:
   - URL: `http://127.0.0.1:5000/ask`
   - Method: POST
   - Body: JSON with a "question" field
   - Example:
     ```
     curl -X POST -H "Content-Type: application/json" -d '{"question":"What is the capital of France?"}' http://127.0.0.1:5000/ask
     ```

Note: Make sure to replace `your_api_key_here` with your actual Anthropic API key.