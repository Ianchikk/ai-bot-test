# 🔹 Folosim Python 3.11
FROM python:3.11

# 🔹 Setăm directorul de lucru
WORKDIR /app

# 🔹 Copiem fișierele necesare
COPY requirements.txt .
COPY . .

# 🔹 Instalăm dependințele
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 Expunem portul 8000
EXPOSE 8000

# 🔹 Comanda pentru a rula serverul FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
