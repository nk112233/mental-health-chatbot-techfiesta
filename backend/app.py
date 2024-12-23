from flask import Flask, request, jsonify, session
from groq import Groq
import os
import json
from flask_cors import CORS

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Set secret key for session encryption
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")
client = Groq(api_key=api_key)

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

        # Process the conversation with Groq
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model="llama3-8b-8192"
        )

        # Access the content directly from the message object
        response_content = chat_completion.choices[0].message.content.strip()

        # Append the assistant's response to the conversation history
        conversation_history.append({"role": "assistant", "content": response_content})

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
