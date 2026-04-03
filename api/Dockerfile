FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh && \
    adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["./entrypoint.sh"]
