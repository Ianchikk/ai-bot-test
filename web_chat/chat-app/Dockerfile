# 🔹 Folosim Node.js
FROM node:18

# 🔹 Setăm directorul de lucru
WORKDIR /app

# 🔹 Copiem fișierele necesare
COPY package.json package-lock.json ./
RUN npm install

COPY . .

# 🔹 Construim aplicația React
RUN npm run build

# 🔹 Expunem portul 3000
EXPOSE 3000

# 🔹 Servim aplicația React
CMD ["npx", "serve", "-s", "build", "-l", "3000"]
