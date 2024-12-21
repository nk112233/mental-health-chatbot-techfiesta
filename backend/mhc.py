import os
from groq import Groq

# Initialize the client with the API key
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Start a chat loop
conversation = [
    {
        "role": "user",
        "content": (
            "You are a chatbot designed to provide mental health support by engaging in empathetic, conversational interactions. "
            "Your goal is to offer calming, compassionate, and non-judgmental advice to help users through emotionally charged or stressful situations. "
            "Keep your language simple, warm, and reassuring, while promoting self-care and positivity."
        )
    }
]

print("Chatbot: Hello! I'm here to listen and offer support. How are you feeling today? (Type 'exit' to quit)\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() in ['exit', 'quit']:
        print("Chatbot: Take care of yourself. Remember, I'm here if you need someone to talk to. 💙")
        break

    # Append user message to the conversation
    conversation.append({
        "role": "user",
        "content": user_input
    })
    
    # Get chatbot response
    chat_completion = client.chat.completions.create(
        messages=conversation,
        model="llama3-8b-8192",
    )
    
    # Get assistant's response
    response = chat_completion.choices[0].message.content
    print(f"\nChatbot: {response}\n")

    # Append the assistant's message to maintain conversation history
    conversation.append({
        "role": "assistant",
        "content": response
    })
