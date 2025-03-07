FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

#EXPOSE 8001 8002 8003

#CMD ["sh", "-c", "cd /app && python main.py"]
