# Dockerfile
FROM python:3.11

COPY . /
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

# Add this line to run the script for creating tables
CMD ["sh", "-c", "python /init/create_tables.py && uvicorn main:app --host 0.0.0.0 --port 8000"]