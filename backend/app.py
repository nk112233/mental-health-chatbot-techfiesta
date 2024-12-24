from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import google.generativeai as genai

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Set secret key for session encryption (not required now but keeping for future use)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

# Initialize Gemini client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")

# Configure Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")
        chat_history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Start a new chat with provided history (if any)
        chat = model.start_chat(history=chat_history)
        
        # Send the latest user message
        response = chat.send_message(user_message)

        # Append new messages to history
        chat_history.append({"role": "user", "parts": user_message})
        chat_history.append({"role": "model", "parts": response.text})

        return jsonify({
            "content": response.text,
            "history": chat_history  # Return updated history for frontend to maintain
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    # Clear chat simply by returning an empty history
    return jsonify({"status": "Chat history cleared.", "history": []})

# if __name__ == '__main__':
#     app.run(debug=True)
