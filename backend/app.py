from flask import Flask, request, jsonify, make_response
from groq import Groq
import os
import json
from flask_cors import CORS

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

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
        "content": "Welcome! I'm here to listen and support you. "
                   "Please feel free to share your thoughts, and I'll provide compassionate guidance."
    }
]

COOKIE_NAME = "chat_history"


def get_user_conversation(request):
    """Retrieve conversation from the cookie, or return the default one."""
    try:
        conversation = request.cookies.get(COOKIE_NAME)
        if conversation:
            return json.loads(conversation)
    except Exception as e:
        print(f"Error loading conversation: {e}")
    return DEFAULT_CONVERSATION[:]


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Retrieve user-specific conversation from the cookie
        conversation_history = get_user_conversation(request)

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

        # Create a response and set the updated conversation in the cookie
        response = make_response(jsonify({"content": response_content}))
        response.set_cookie(COOKIE_NAME, json.dumps(conversation_history), httponly=True, max_age=60*60*24*7)

        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    conversation = get_user_conversation(request)
    return jsonify({"history": conversation[2:]})  # Skip the first two responses


@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    response = make_response(jsonify({"status": "Chat history cleared for this user."}))
    response.set_cookie(COOKIE_NAME, json.dumps(DEFAULT_CONVERSATION), httponly=True, max_age=60*60*24*7)
    return response


# if __name__ == '__main__':
#     app.run(debug=True)
