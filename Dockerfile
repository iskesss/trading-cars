FROM python:3.12-slim-bookworm

WORKDIR /app

EXPOSE 8080

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . . 

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

# HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health

CMD sh -c "streamlit run frontend.py \
    --server.port=${PORT:-8080} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.baseUrlPath=''"

