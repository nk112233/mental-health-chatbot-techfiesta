from flask import Flask, request, jsonify
from groq import Groq
import os
from flask_cors import CORS

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")
client = Groq(api_key=api_key)

# Store the conversation state globally (for demo purposes, use session or DB in production)
conversation_history = [
    {
        "role": "user",
        "content": "You are a chatbot designed to provide mental health support. "
                   "Keep your responses calming and empathetic."
    },
    {
        "role": "assistant",
        "content": "Welcome! I'm here to listen and support you with your mental health concerns. My purpose is to provide a safe and non-judgmental space for you to express yourself, and I'm here to help you manage your mental well-being.\n\nPlease know that everything discussed in our chat is confidential and anonymous. I'm not a replacement for professional help, but I can offer guidance, resources, and support to help you feel more comfortable and empowered to take care of your mental health.\n\nWhat's been going on lately that's been worrying or stressing you out? Is there anything specific you'd like to talk about or share with me?"
    }
]

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

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

        return jsonify({"content": response_content})

    except Exception as e:
        print(f"Error: {str(e)}")  # Print error details for debugging
        return jsonify({"error": str(e)}), 500


# Endpoint to get the current chat history (excluding the first two responses)
@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    return jsonify({"history": conversation_history[2:]})  # Skip the first two responses


# Endpoint to clear the chat history, but keep the first two messages
@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    global conversation_history
    conversation_history = conversation_history[:2]  # Retain only the first two responses
    return jsonify({"status": "Chat history cleared, first two responses retained."})


# if __name__ == '__main__':
#     app.run()
