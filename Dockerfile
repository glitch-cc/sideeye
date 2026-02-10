FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY *.py /app/

EXPOSE 5006

CMD ["python", "web_app.py"]
