# Folosim o imagine Python oficială
FROM python:3.11

# Setăm directorul de lucru în container
WORKDIR /app

# Copiem fișierele proiectului
COPY . .

# Instalăm dependențele
RUN pip install --no-cache-dir -r requirements.txt

# Definim comanda de rulare
CMD ["python", "main.py"]