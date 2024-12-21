from flask import Flask, request, jsonify, session
from groq import Groq
import os
from flask_cors import CORS

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

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
    },
    {
        "role": "assistant",
        "content": "Welcome! I'm here to listen and support you with your mental health concerns. "
                   "Please feel free to share your thoughts, and I'll provide compassionate guidance."
    }
]


def get_user_conversation():
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

        # Retrieve user-specific conversation history
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

        # Update session with the new conversation
        session['conversation'] = conversation_history

        return jsonify({"content": response_content})

    except Exception as e:
        print(f"Error: {str(e)}")  # Print error details for debugging
        return jsonify({"error": str(e)}), 500


# Endpoint to get the current chat history (excluding the initial system prompts)
@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    conversation = get_user_conversation()
    return jsonify({"history": conversation[2:]})  # Skip the first two responses


# Endpoint to clear the chat history but retain initial system messages
@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    session['conversation'] = DEFAULT_CONVERSATION[:]
    return jsonify({"status": "Chat history cleared for this user."})


# if __name__ == '__main__':
#     app.run(debug=True)
