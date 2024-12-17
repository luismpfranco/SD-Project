import grpc
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
import time
import logging
import signal
import sys
from prometheus_client import start_http_server, Counter, Histogram, Gauge

logging.basicConfig(level=logging.INFO)

REQUEST_COUNT = Counter('product_service_requests_total', 'Total number of requests to the product service')
REQUEST_LATENCY = Histogram('product_service_request_latency_seconds', 'Request latency in seconds', ['method'])
ERROR_COUNT = Counter('product_service_errors_total', 'Total number of errors in the product service')
UPTIME_GAUGE = Gauge('product_service_uptime_seconds', 'Uptime of the product service in seconds')

class ProductServicer(product_service_pb2_grpc.ProductServiceServicer):
    def __init__(self):
        self.products = []
        self.start_time = time.time()
        logging.info("ProductServicer initialized")

    def GetHealth(self, request, context):
        uptime = time.time() - self.start_time
        UPTIME_GAUGE.set(uptime)
        version = "1.0.0"
        return product_service_pb2.HealthCheckResponse(
            status=f"ok - Uptime: {uptime:.2f} seconds",
            version=version
        )

    def GetProducts(self, request, context):
        start_time = time.time()
        REQUEST_COUNT.inc()
        
        # Simular algum processamento
        time.sleep(0.1)

        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method='GetProducts').observe(latency)
        
        logging.info(f"GetProducts requested. Returning {len(self.products)} products")
        return product_service_pb2.GetProductsResponse(products=self.products)

    def GetProductById(self, request, context):
        product = next((p for p in self.products if p.id == request.id), None)
        if product:
            return product
        
        ERROR_COUNT.inc()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        return product_service_pb2.Product()

    def AddProduct(self, request, context):
        new_product = request.product
        new_product.id = len(self.products) + 1
        self.products.append(new_product)
        
        return product_service_pb2.StandardResponse(
            success=True,
            message=f"Product added with ID: {new_product.id}"
        )

    def UpdateProduct(self, request, context):
        product = next((p for p in self.products if p.id == request.product.id), None)
        
        if product:
            product.CopyFrom(request.product)
            return product
        
        ERROR_COUNT.inc()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        
    def DeleteProduct(self, request, context):
        product = next((p for p in self.products if p.id == request.id), None)
        
        if product:
            self.products.remove(product)
            return product_service_pb2.StandardResponse(success=True, message="Product deleted")
        
        ERROR_COUNT.inc()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        
def signal_handler(sig, frame):
    logging.info('Você pressionou Ctrl+C! Encerrando o servidor...')
    server.stop(0)
    sys.exit(0)

def serve():
    start_http_server(8000)
    global server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    
    logging.info("Servidor iniciado. Ouvindo na porta 50051.")
    
    signal.signal(signal.SIGINT, signal_handler)

    try:
       server.wait_for_termination()
    except KeyboardInterrupt:
       logging.info("Interrupção de teclado recebida. Encerrando o servidor...")
       server.stop(0)

if __name__ == '__main__':
   serve()
