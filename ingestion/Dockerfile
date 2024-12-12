# Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN pip install irc requests python-dotenv

COPY . .

CMD ["python", "ingestion.py"]