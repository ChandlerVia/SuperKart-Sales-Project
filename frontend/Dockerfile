FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy dependency definitions
COPY requirements.txt .

# Install frontend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit application
COPY app.py .

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
