FROM python:3.11-alpine
WORKDIR /app

# Instalar dependências de build necessárias para alguns pacotes Python
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
USER 1000:1000
CMD ["python", "app.py"]
