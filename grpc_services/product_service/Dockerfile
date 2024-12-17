# Usar uma imagem base do Python
FROM python:3.12-slim

# Install the necessary dependencies
RUN pip install grpcio grpcio-tools

# Copy the service files
COPY . /app

# Set the working directory
WORKDIR /app

# Instalar as dependências necessárias diretamente
RUN pip install --no-cache-dir grpcio grpcio-tools prometheus_client

# Expor a porta que o gRPC usará
EXPOSE 50051

# Comando para iniciar o servidor gRPC
CMD ["python", "server.py"]