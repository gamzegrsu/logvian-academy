FROM python:3.10-slim

WORKDIR /app
COPY app.py wordlist.txt vulnerable_hash.txt /app/

RUN pip install flask

CMD ["python", "app.py"]
