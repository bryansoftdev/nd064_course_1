FROM python:3.8

EXPOSE 3111

WORKDIR /app
COPY ./techtrends /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python init_db.py

CMD ["python", "app.py"]
