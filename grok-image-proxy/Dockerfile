FROM python:3.12-slim
RUN pip install --no-cache-dir requests
WORKDIR /app
COPY proxy.py .
CMD ["python", "proxy.py"]
