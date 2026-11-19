FROM python:3.13-slim

# Set the application's working directory
WORKDIR /app

# Copy the backend files into the container
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Document the API port
EXPOSE 7860

# Start the Flask API using Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "app:superkart_api"]
