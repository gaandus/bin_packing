FROM python:3.9-slim

WORKDIR /app

# Install dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data && chmod 777 /app/data

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production

# Expose the port
EXPOSE 5000

# Run the application with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "web_app:app", "--workers", "2", "--timeout", "60"] 