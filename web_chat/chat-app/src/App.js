import React, { useState, useEffect } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [socket, setSocket] = useState(null);

  // Conectăm WebSocket la serverul FastAPI
  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat");

    ws.onmessage = (event) => {
      setMessages((prevMessages) => [...prevMessages, { text: event.data, sender: "bot" }]);
    };

    ws.onclose = () => console.log("❌ Conexiunea WebSocket s-a închis");

    setSocket(ws);

    return () => ws.close();
  }, []);

  // Trimiterea mesajului către WebSocket
  const sendMessage = () => {
    if (socket && input.trim() !== "") {
      socket.send(input);
      setMessages((prevMessages) => [...prevMessages, { text: input, sender: "user" }]);
      setInput("");
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "auto", padding: "20px", textAlign: "center" }}>
      <h2>💬 Chat AI</h2>
      <div style={{ border: "1px solid #ddd", padding: "10px", minHeight: "200px" }}>
        {messages.map((msg, index) => (
          <p key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left", color: msg.sender === "user" ? "blue" : "green" }}>
            {msg.text}
          </p>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Scrie un mesaj..."
      />
      <button onClick={sendMessage}>📩 Trimite</button>
    </div>
  );
}

export default App;
