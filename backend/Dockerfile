FROM python:3.11-slim

WORKDIR /app

# System deps needed by PyMuPDF / torch / faiss build chains
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the spaCy English model so it's baked into the image
RUN python -m spacy download en_core_web_sm

COPY . .

RUN mkdir -p /app/data /app/uploads /app/uploads/exports /app/data/vector_store

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
