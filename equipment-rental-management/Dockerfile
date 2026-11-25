# Use an official Python base image.
FROM python:3.11-slim

# Set the working directory.
WORKDIR /app

# Install the application dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files.
COPY app/ ./app/
COPY run.py notification_service.py ./

# Expose the Flask application port.
EXPOSE 5000

# Start the Flask application.
CMD ["python", "-m", "flask", "--app", "run", "run", "--host", "0.0.0.0", "--port", "5000"]
