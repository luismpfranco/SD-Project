FROM python:3.11-slim

WORKDIR /app

# Copy the service files
COPY . /app

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. product_service.proto

EXPOSE 3002 3003

ENV PYTHONUNBUFFERED=1
ENV GRPC_PORT=3002
ENV HEALTH_PORT=3003

CMD ["python", "server.py"]
