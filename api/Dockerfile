FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files and directories
COPY main.py .
COPY config.py .
COPY database.py .
COPY models/ ./models/
COPY controllers/ ./controllers/
COPY routers/ ./routers/
COPY templates/ ./templates/

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
