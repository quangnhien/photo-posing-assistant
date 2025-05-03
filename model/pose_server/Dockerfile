# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
# Copy code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Expose port
EXPOSE 8003

# Run server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]