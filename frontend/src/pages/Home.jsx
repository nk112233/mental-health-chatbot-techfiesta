import axios from "axios";
import { useState, useEffect, useRef } from "react";

export default function Home() {
    const [messages, setMessages] = useState([
        { role: "assistant", content: "How can I help you today?" } // Initial assistant message
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const firstAssistantMessageRef = useRef(null);

    // Axios instance with credentials
    const api = axios.create({
        baseURL: "https://mental-health-chatbot-api.vercel.app",
        withCredentials: true,  // Keep this if cookies are required for API
    });

    // Fetch chat history from localStorage on load
    useEffect(() => {
        const storedMessages = JSON.parse(localStorage.getItem("chatHistory"));
        if (storedMessages) {
            setMessages(storedMessages);
        }
    }, []);

    // Send message to Flask backend
    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { role: "user", content: input };
        const updatedMessages = [...messages, userMessage];

        // Update frontend immediately
        setMessages(updatedMessages);
        localStorage.setItem("chatHistory", JSON.stringify(updatedMessages));

        setInput("");
        setLoading(true);

        try {
            const response = await api.post("/chat", {
                message: input,
                history: updatedMessages.map((msg) => ({
                    role: msg.role,
                    parts: msg.content,  // Match Flask history format
                })),
            });

            // Append assistant's response
            const assistantMessage = { role: "assistant", content: response.data.content };
            const newHistory = [...updatedMessages, assistantMessage];

            setMessages(newHistory);
            localStorage.setItem("chatHistory", JSON.stringify(newHistory));
        } catch (error) {
            console.error("Error sending message:", error);
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
            await api.post("/clear-chat");  // Inform backend if necessary
            setMessages([{ role: "assistant", content: "How can I help you today?" }]);
            localStorage.removeItem("chatHistory");
        } catch (error) {
            console.error("Failed to clear chat:", error);
        }
    };

    // Scroll to the latest assistant message
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
                                    dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, "<br />") }}
                                />
                            </div>
                        ))
                    )}
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
