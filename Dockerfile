FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "python main.py"]

#CMD ["sh", "-c", "cd /app && python main.py"]
