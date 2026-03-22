FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt
RUN pip install sentence-transformers==3.0.1 transformers==4.44.2

COPY app ./app
COPY knowledge ./knowledge
COPY main.py .
RUN mkdir /models

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
