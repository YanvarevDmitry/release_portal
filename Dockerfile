# Dockerfile
FROM python:3.11

ENV DATABASE_URL=postgresql://postgres:password@db:5432/postgres

COPY . /


RUN pip install -r  requirements.txt --system

WORKDIR /app

# Add this line to run the script for creating tables
CMD ["sh", "-c", "python create_tables.py && uvicorn main:app --host 0.0.0.0 --port 8000 --loop uvloop --http httptools"]