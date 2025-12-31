FROM python:3.11-slim

# Install FFmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=True

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY app.py /app/app.py

COPY multi_tools_agent/__init__.py /app/multi_tools_agent/__init__.py
COPY multi_tools_agent/agent.py /app/multi_tools_agent/agent.py
COPY multi_tools_agent/prompt /app/multi_tools_agent/prompt
#COPY multi_tools_agent/tools /app/multi_tools_agent/tools

# Expose API port
EXPOSE 8080

# Run the application
#CMD ["ddtrace-run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

