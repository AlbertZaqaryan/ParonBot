FROM python:3.11-alpine

WORKDIR /app

# Устанавливаем системные зависимости (очень важно для Alpine)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Копируем только requirements сначала (кэшируется)
COPY requirements.txt .

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем проект (venv будет проигнорен через .dockerignore)
COPY . .

CMD ["python", "bot.py"]