FROM tiangolo/uvicorn-gunicorn-fastapi:python3.13

WORKDIR /maadb-2024

COPY./app /app
