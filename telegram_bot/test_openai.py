import openai
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()

# Inițializăm clientul OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Schimbă din gpt-4 în gpt-3.5-turbo
        messages=[{"role": "user", "content": "Explică ce este inteligența artificială"}]
    )
    print("✅ Răspuns OpenAI:", response.choices[0].message.content)
except Exception as e:
    print("❌ Eroare OpenAI:", e)
