from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")

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

        # Prepare chat history for the Gemini model
        formatted_history = [
            {"role": "user", "parts": msg["parts"]} if msg["role"] == "user" else
            {"role": "model", "parts": msg["parts"]}
            for msg in chat_history
        ]

        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(user_message)

        # Append user and assistant messages to history
        chat_history.append({"role": "user", "parts": user_message})
        chat_history.append({"role": "assistant", "parts": response.text})

        return jsonify({
            "content": response.text,
            "history": chat_history  # Return updated history
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    return jsonify({"status": "Chat history cleared.", "history": []})

# if __name__ == '__main__':
#     app.run(debug=True)