# 🐍 Минималистичный Python-образ
FROM python:3.11-slim

# 🧪 Устанавливаем рабочую директорию
WORKDIR /app

# 📄 Копируем только requirements сначала (для кэширования зависимостей)
COPY requirements.txt .

# ⚙️ Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 🗂 Копируем остальной проект
COPY . .

# 🚀 Запуск FastAPI через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
