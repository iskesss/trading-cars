FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . . 

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

ENV PORT=8080
EXPOSE ${PORT}

HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health

CMD streamlit run frontend.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.baseUrlPath=""
