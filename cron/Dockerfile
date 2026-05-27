FROM python:3.12-alpine

WORKDIR /opt/chatbot-monitoring

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chatbot_sync.py chatbot_daily_report.py ./

ENV SQLITE_PATH=/app/prisma/data/chatbot.db

ENTRYPOINT ["python"]
