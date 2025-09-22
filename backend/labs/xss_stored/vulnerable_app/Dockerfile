FROM python:3.10-slim

WORKDIR /app
COPY app.py requirements.txt /app/

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
