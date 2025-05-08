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


# Expose port
EXPOSE 8003

# Run the model download script
#RUN python download_model.py
# Run server

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]