import openai
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()

# 🔹 Preluăm cheia API OpenAI din fișierul .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Inițializăm clientul OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def ask_openai(prompt: str) -> str:
    """ Trimite o întrebare către OpenAI și returnează răspunsul """
    try:
        print(f"📨 Întrebare trimisă către OpenAI: {prompt}")  # Debugging

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Poți folosi "gpt-4" dacă ai acces
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content
        print(f"✅ Răspuns OpenAI primit: {answer}")  # Debugging
        return answer

    except Exception as e:
        print(f"❌ Eroare OpenAI: {e}")  # Debugging
        return f"❌ Eroare OpenAI: {e}"
