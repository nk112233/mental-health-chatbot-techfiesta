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


def get_user_conversation():
    """Retrieve conversation from session, or return default."""
    if 'conversation' not in session:
        session['conversation'] = DEFAULT_CONVERSATION[:]
    return session['conversation']


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Retrieve user-specific conversation from the session
        conversation_history = get_user_conversation()

        # Append the new user message to the conversation history
        conversation_history.append({"role": "user", "content": user_message})

        # Prepare the input for Gemini
        input_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])

        # Generate response using Gemini
        response = genai.generate_text(
            model="gemini-pro",
            prompt=input_text
        )

        # Extract response content
        response_content = response.result.strip()

        # Append the assistant's response to the conversation history
        response_content_bidu = f"Act like a bidu bindast guy. {response_content}"
        conversation_history.append({"role": "assistant", "content": response_content_bidu})

        # Save the updated conversation to the session
        session['conversation'] = conversation_history
        session.modified = True

        return jsonify({"content": response_content})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    conversation = get_user_conversation()
    return jsonify({"history": conversation[2:]})


@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    session['conversation'] = DEFAULT_CONVERSATION[:]
    session.modified = True
    return jsonify({"status": "Chat history cleared for this user."})


# if __name__ == '__main__':
#     app.run(debug=True)
