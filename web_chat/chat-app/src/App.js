import React from "react";
import { useForm } from "react-hook-form";
import axios from "axios";

function App() {
  // Hook pentru gestionarea formularului
  const { register, handleSubmit, formState: { errors } } = useForm();

  // Funcție pentru trimiterea datelor către backend
  const onSubmit = async (data) => {
    try {
      const response = await axios.post("http://localhost:8000/register", data);
      alert("✅ Datele au fost trimise cu succes!");
      console.log("Răspuns server:", response.data);
    } catch (error) {
      alert("❌ Eroare la trimiterea datelor!");
      console.error("Eroare:", error);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "auto", padding: "20px", textAlign: "center" }}>
      <h2>📝 Înregistrează-te</h2>
      <form onSubmit={handleSubmit(onSubmit)}>

        {/* Câmp pentru nume */}
        <div>
          <label>Nume:</label>
          <input {...register("name", { required: "Numele este obligatoriu" })} />
          {errors.name && <p style={{ color: "red" }}>{errors.name.message}</p>}
        </div>

        {/* Câmp pentru telefon */}
        <div>
          <label>Telefon:</label>
          <input {...register("phone", { required: "Telefonul este obligatoriu" })} />
          {errors.phone && <p style={{ color: "red" }}>{errors.phone.message}</p>}
        </div>

        {/* Câmp pentru email */}
        <div>
          <label>Email:</label>
          <input {...register("email", { required: "Emailul este obligatoriu", pattern: { value: /^\S+@\S+$/i, message: "Email invalid" } })} />
          {errors.email && <p style={{ color: "red" }}>{errors.email.message}</p>}
        </div>

        {/* Buton Submit */}
        <button type="submit">📩 Trimite</button>
      </form>
    </div>
  );
}

export default App;
