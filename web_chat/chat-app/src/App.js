import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";

function App() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [isRegistered, setIsRegistered] = useState(false);
  const [chatEnabled, setChatEnabled] = useState(false);
  const [dealId, setDealId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [socket, setSocket] = useState(null);

  // Înregistrare utilizator și conectare la WebSocket
  const onSubmit = async (data) => {
    try {
      const response = await axios.post("http://localhost:8000/register", data);
      const newDealId = response.data.deal_id;

      if (!newDealId) {
        throw new Error("❌ Eroare: Deal ID invalid.");
      }

      setIsRegistered(true);
      setChatEnabled(true);
      setDealId(newDealId);

      // Conectare WebSocket pentru utilizator
      connectUser(newDealId);
    } catch (error) {
      alert("❌ Eroare la înregistrare!");
      console.error("Eroare:", error);
    }
  };

  // Funcție pentru a conecta utilizatorul la WebSocket
  const connectUser = (dealId) => {
    if (socket) {
      socket.close(); // Închide conexiunea existentă, dacă există
    }

    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/chat/user/${dealId}`);

    ws.onopen = () => console.log("✅ WebSocket utilizator conectat.");
    ws.onmessage = (event) => {
      setMessages((prevMessages) => [...prevMessages, { text: event.data, sender: "bot" }]);
    };
    ws.onerror = (error) => console.error("❌ Eroare WebSocket utilizator:", error);
    ws.onclose = () => console.log("❌ Conexiunea WebSocket utilizator s-a închis.");

    setSocket(ws);
  };

  // Funcție pentru a conecta managerul la WebSocket
  const connectManager = async () => {
    if (!dealId) {
      alert("⚠️ Deal ID invalid. Înregistrează-te mai întâi.");
      return;
    }
  
    try {
      await axios.post(`http://localhost:8000/notify_manager/${dealId}`);
  
      const ws = new WebSocket(`ws://127.0.0.1:8000/ws/chat/manager/${dealId}`);
  
      ws.onopen = () => console.log("✅ WebSocket manager conectat.");
      ws.onmessage = (event) => {
        setMessages((prevMessages) => [...prevMessages, { text: event.data, sender: "manager" }]);
      };
      ws.onerror = (error) => console.error("❌ Eroare WebSocket manager:", error);
      ws.onclose = () => console.log("❌ Conexiunea WebSocket manager s-a închis.");
  
      setSocket(ws);
    } catch (error) {
      console.error("❌ Eroare la trimiterea notificării în Bitrix24:", error);
    }
  };
  

  // Trimite mesaj în chat
  const sendMessage = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      alert("⚠️ Conexiunea WebSocket nu este deschisă.");
      return;
    }

    if (input.trim() === "") {
      return;
    }

    socket.send(JSON.stringify({ message: input, deal_id: dealId }));
    setMessages((prevMessages) => [...prevMessages, { text: input, sender: "user" }]);
    setInput("");
  };

  return (
    <div style={{ maxWidth: "600px", margin: "auto", padding: "20px", textAlign: "center" }}>
      {!isRegistered ? (
        <>
          <h2>📝 Înregistrează-te</h2>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label>Nume:</label>
              <input {...register("name", { required: "Numele este obligatoriu" })} />
              {errors.name && <p style={{ color: "red" }}>{errors.name.message}</p>}
            </div>

            <div>
              <label>Telefon:</label>
              <input {...register("phone", { required: "Telefonul este obligatoriu" })} />
              {errors.phone && <p style={{ color: "red" }}>{errors.phone.message}</p>}
            </div>

            <div>
              <label>Email:</label>
              <input {...register("email", { required: "Emailul este obligatoriu" })} />
              {errors.email && <p style={{ color: "red" }}>{errors.email.message}</p>}
            </div>

            <button type="submit">📩 Trimite</button>
          </form>
        </>
      ) : (
        <>
          <h2>💬 Chat AI</h2>
          <div style={{ border: "1px solid #ddd", padding: "10px", minHeight: "200px" }}>
            {messages.map((msg, index) => (
              <p key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left", color: msg.sender === "user" ? "blue" : msg.sender === "bot" ? "green" : "red" }}>
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
          <button onClick={connectManager} style={{ marginLeft: "10px" }}>👔 Conectează Manager</button>
        </>
      )}
    </div>
  );
}

export default App;
