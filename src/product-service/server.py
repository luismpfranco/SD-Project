import grpc
from concurrent import futures
import product_pb2
import product_pb2_grpc
import os
import uuid
import logging
from typing import Dict, List
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time
from concurrent import futures
import time
import logging
import signal
import sys
from data import INITIAL_PRODUCTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

REQUEST_COUNT = Counter('product_service_requests_total', 'Total number of requests to the product service')
REQUEST_LATENCY = Histogram('product_service_request_latency_seconds', 'Request latency in seconds', ['method'])
ERROR_COUNT = Counter('product_service_errors_total', 'Total number of errors in the product service')
UPTIME_GAUGE = Gauge('product_service_uptime_seconds', 'Uptime of the product service in seconds')

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            health_response = {
                "status": "ok",
                "version": os.getenv("APP_VERSION", "0.1.0")
            }
            self.wfile.write(json.dumps(health_response).encode())
        else:
            self.send_response(404)
            self.end_headers()

class ProductServicer(product_pb2_grpc.ProductServiceServicer):
    def __init__(self):
        self.products: Dict[str, product_pb2.Product] = {}
        # Load initial products
        for product_data in INITIAL_PRODUCTS:
            product = product_pb2.Product(**product_data)
            self.products[product.id] = product
        logging.info(f"Initialized with {len(self.products)} products")

    def GetProducts(self, request, context):
        logging.info("Received GetProducts request")
        start_time = time.time()
        REQUEST_COUNT.inc()
        # Simular algum processamento
        time.sleep(0.1)
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method='GetProducts').observe(latency)
        logging.info(f"GetProducts requested. Returning {len(self.products)} products. Latency: {latency:.2f} seconds")
        return product_pb2.ProductList(products=list(self.products.values()))

    def GetProduct(self, request, context):
        logging.info(f"Received GetProduct request for ID: {request.id}")
        if request.id not in self.products:
            logging.warning(f"Product not found: {request.id}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Product not found')
            return product_pb2.Product()
        return self.products[request.id]

    def CreateProduct(self, request, context):
        product_id = str(uuid.uuid4())
        product = product_pb2.Product(
            id=product_id,
            name=request.name,
            description=request.description,
            price=request.price,
            image_url=request.image_url,
            available=request.available
        )
        self.products[product_id] = product
        return product

    def UpdateProduct(self, request, context):
        if request.id not in self.products:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Product not found')
            return product_pb2.Product()
        self.products[request.id] = request
        return request

    def DeleteProduct(self, request, context):
        if request.id not in self.products:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Product not found')
            return product_pb2.Empty()
        del self.products[request.id]
        return product_pb2.Empty()
    
def signal_handler(sig, frame):
    logging.info('Você pressionou Ctrl+C! Encerrando o servidor...')
    server.stop(0)
    sys.exit(0)

def serve():
    # Start health check server on port 3003
    health_port = int(os.getenv('HEALTH_PORT', '3003'))
    health_server = HTTPServer(('', health_port), HealthCheckHandler)
    health_thread = threading.Thread(target=health_server.serve_forever)
    health_thread.daemon = True
    health_thread.start()
    logging.info(f"Health check server started on port {health_port}")

    # Start gRPC server on port 3002
    grpc_port = int(os.getenv('GRPC_PORT', '3002'))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(
        ProductServicer(), server
    )
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    logging.info(f"gRPC Server started on port {grpc_port}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()