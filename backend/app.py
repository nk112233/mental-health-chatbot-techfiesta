from flask import Flask, request, jsonify, session
import os
import json
from flask_cors import CORS
import google.generativeai as genai

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Set secret key for session encryption
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

# Initialize Gemini client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")

# Configure the Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Default initial conversation state
DEFAULT_CONVERSATION = [
    {
        "role": "user",
        "content": "You are a chatbot designed to provide mental health support. "
                   "Keep your responses calming and empathetic."
                   "You are Built by Passionate AI Engineers."
                   "Act like a bidu bindast boy."
    },
    {
        "role": "assistant",
        "content": "Welcome! I'm here to listen and support you. "
                   "Please feel free to share your thoughts, and I'll provide compassionate guidance."
    }
]

# Ensure the session is initialized properly
@app.before_request
def initialize_conversation():
    if "conversation" not in session:
        session["conversation"] = DEFAULT_CONVERSATION

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Get the conversation from session
        conversation = session["conversation"]

        # Prepare the input for Gemini
        input_text = f"user: {user_message}"

        # Add user message to conversation
        conversation.append({
            "role": "user",
            "content": user_message
        })

        # Generate response using Gemini
        response = model.generate_content(input_text)

        # Extract response content
        response_content = response.text.strip()

        # Add assistant response to conversation
        conversation.append({
            "role": "assistant",
            "content": response_content
        })

        # Save updated conversation back to session
        session["conversation"] = conversation

        return jsonify({"content": response_content})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    # Clear the conversation in session
    session.pop("conversation", None)
    return jsonify({"status": "Chat history cleared."})

if __name__ == '__main__':
    app.run(debug=True)
