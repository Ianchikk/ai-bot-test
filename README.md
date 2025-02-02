
🚀 1. Cerințe Prealabile
Înainte de a începe, asigurățivă că aveți instalat:
- Git
- Docker & Docker Compose

📥 2. Clonare Repository
Clonați proiectul pe server sau pe mașina locală:
git clone https://github.com/Ianchikk/ai-bot-test.git
cd ai-bot-test

⚙️ 3. Configurare Variabile de Mediu
Înainte de a rula aplicația, trebuie să configurați variabilele de mediu.
- În mapa /telegram_bot/docker-compose.yml - configurați
variabilele de mediu (environment:)
- Și în mapa /web_chat/docker-compose.yml - la fel
    Sau creați in fiecare mapă fișierul .env

🐳 4. Construire și Pornire Containere Docker
Rulați următoarele comande pentru a construi și porni containerele:
1. Pentru tg bot:
    cd telegram_bot
    docker-compose up --build -d
2. Pentru web-chat:
    cd ..
    cd web_chat
    docker-compose up --build -d
