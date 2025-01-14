# Dockerfile
FROM python:3.11

COPY . /
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Add this line to run the script for creating tables
CMD ["sh", "-c", "python app/init/create_tables.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]