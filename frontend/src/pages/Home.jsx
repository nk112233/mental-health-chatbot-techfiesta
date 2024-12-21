import { useState, useEffect, useRef } from "react";

export default function Home() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    // Create a ref to track the first assistant message
    const firstAssistantMessageRef = useRef(null);

    // Fetch the chat history when the component mounts
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await fetch(`https://mental-health-chatbot-api.vercel.app/chat-history`);
                if (response.ok) {
                    const data = await response.json();
                    console.log(data.history);
                    setMessages(data.history || []);
                }
            } catch (error) {
                console.error("Error fetching chat history:", error);
            }
        };
        fetchHistory();
    }, []);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { role: "user", content: input };

        // Add user's message to the chat
        setMessages((prevMessages) => [...prevMessages, userMessage]);

        // Clear input field after message is sent
        setInput("");
        setLoading(true);

        try {
            const response = await fetch(`https://mental-health-chatbot-api.vercel.app/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: input }),
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }

            const data = await response.json();

            // Add bot's response to the chat
            setMessages((prevMessages) => [
                ...prevMessages,
                { role: "assistant", content: data.content },
            ]);
        } catch (error) {
            console.error("Error:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { role: "assistant", content: "Oops! Something went wrong. Please try again." },
            ]);
        } finally {
            setLoading(false);
        }
    };

    // Clear chat history
    const clearChat = async () => {
        try {
            const response = await fetch(`https://mental-health-chatbot-api.vercel.app/clear-chat`, { method: "POST" });
            if (response.ok) {
                // Fetch new history excluding the first two responses
                const newHistoryResponse = await fetch(`https://mental-health-chatbot-api.vercel.app/chat-history`);
                if (newHistoryResponse.ok) {
                    const newHistoryData = await newHistoryResponse.json();
                    setMessages(newHistoryData.history || []);
                }
            } else {
                console.error("Failed to clear chat.");
            }
        } catch (error) {
            console.error("Error clearing chat:", error);
        }
    };

    // Scroll to the first assistant message after each message update
    useEffect(() => {
        if (firstAssistantMessageRef.current) {
            firstAssistantMessageRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    return (
        <div className="min-h-screen bg-blue-50 flex justify-center items-center p-4">
            <div className="w-full max-w-4xl bg-white shadow-lg rounded-lg p-6">
                <h1 className="text-3xl font-bold text-center text-blue-600 mb-6">
                    Mental Health Chatbot 💬
                </h1>

                <div className="h-96 overflow-y-auto border p-4 rounded mb-4">
                    {messages.length === 0 ? (
                        <p className="text-center text-gray-500">Start a conversation...</p>
                    ) : (
                        messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`mb-2 ${msg.role === "user" ? "text-right" : "text-left"}`}
                            >
                                <span
                                    className={`inline-block px-4 py-2 rounded-lg ${
                                        msg.role === "user"
                                            ? "bg-blue-500 text-white"
                                            : "bg-gray-200"
                                    }`}
                                    // Render content with newline characters as HTML
                                    dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, "<br />") }}
                                />
                            </div>
                        ))
                    )}

                    {/* Scroll to the first assistant message */}
                    {messages.find((msg) => msg.role === "assistant") && (
                        <div ref={firstAssistantMessageRef} />
                    )}
                </div>

                <div className="flex items-center space-x-4">
                    <input
                        type="text"
                        className="flex-grow p-3 border rounded-lg focus:outline-none"
                        placeholder="Type a message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                    />
                    <button
                        className={`${
                            loading ? "bg-gray-400" : "bg-blue-500 hover:bg-blue-600"
                        } text-white px-6 py-3 rounded-lg`}
                        onClick={sendMessage}
                        disabled={loading}
                    >
                        {loading ? "Thinking..." : "Send"}
                    </button>
                    <button
                        className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg"
                        onClick={clearChat}
                    >
                        Clear Chat
                    </button>
                </div>
            </div>
        </div>
    );
}
