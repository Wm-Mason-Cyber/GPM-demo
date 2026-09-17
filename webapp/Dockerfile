FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV SITE_KEY=bank
EXPOSE 5000 5001

CMD ["sh", "-c", "python app.py ${SITE_KEY}"]
