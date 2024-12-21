from flask import Flask, request, jsonify, session
from groq import Groq
import os
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-secret-key")

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")
client = Groq(api_key=api_key)

DEFAULT_CONVERSATION = [
    {
        "role": "user",
        "content": "You are a chatbot designed to provide mental health support. "
                   "Keep your responses calming and empathetic."
    },
    {
        "role": "assistant",
        "content": "Welcome! I'm here to listen and support you with your mental health concerns. "
                   "Please feel free to share your thoughts, and I'll provide compassionate guidance."
    }
]


def get_user_conversation():
    # Check if session exists, if not create a new conversation for user
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

        conversation_history = get_user_conversation()
        conversation_history.append({"role": "user", "content": user_message})

        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model="llama3-8b-8192"
        )

        response_content = chat_completion.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": response_content})

        # Save updated conversation in session
        session['conversation'] = conversation_history

        return jsonify({"content": response_content})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    conversation = get_user_conversation()
    return jsonify({"history": conversation[2:]})  # Skip the initial prompt


@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    session['conversation'] = DEFAULT_CONVERSATION[:]
    return jsonify({"status": "Chat history cleared for this user."})


if __name__ == '__main__':
    app.run(debug=True)
