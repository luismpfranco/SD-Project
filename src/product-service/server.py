import grpc
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
import time
import logging
import signal
import sys
from prometheus_client import start_http_server, Counter, Histogram, Gauge
from product_repository import ProductRepository

logging.basicConfig(level=logging.INFO)

# Contadores e métricas
REQUEST_COUNT = Counter('product_service_requests_total', 'Total number of requests to the product service')
REQUEST_LATENCY = Histogram('product_service_request_latency_seconds', 'Request latency in seconds', ['method'])
ERROR_COUNT = Counter('product_service_errors_total', 'Total number of errors in the product service')
UPTIME_GAUGE = Gauge('product_service_uptime_seconds', 'Uptime of the product service in seconds')
UPDATE_COUNT = Counter('product_service_updates_total', 'Total number of product updates')
DELETE_COUNT = Counter('product_service_deletes_total', 'Total number of products deleted')
PRODUCT_COUNT = Gauge('product_service_product_count', 'Current number of products in the service')

class ProductServicer(product_service_pb2_grpc.ProductServiceServicer):
    def __init__(self):
        self.products = []
        self.repository = ProductRepository()
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
        #REQUEST_COUNT.inc()

        # Simular algum processamento
        time.sleep(0.1)

        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method='GetProducts').observe(latency)

        products = [product_service_pb2.Product(**p) for p in self.repository.get_products()]
        PRODUCT_COUNT.set(len(products))  # Atualiza a contagem de produtos
        logging.info(f"GetProducts requested. Returning {len(products)} products")
        return product_service_pb2.GetProductsResponse(products=products)

    def GetProductById(self, request, context):
        product_dict = self.repository.get_product_by_id(request.id)
        if product_dict:
            return product_service_pb2.Product(**product_dict)

        ERROR_COUNT.inc()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        return product_service_pb2.Product()

    def AddProduct(self, request, context):
        new_product = request.product
        new_product.id = len(self.repository.get_products()) + 1  # A lógica de ID deve ser ajustada no repositório.
        self.repository.add_product(new_product)
        REQUEST_COUNT.inc()

        return product_service_pb2.StandardResponse(
            success=True,
            message=f"Product added with ID: {new_product.id}"
        )

    def UpdateProduct(self, request, context):
        updated = self.repository.update_product(request.product)
        if updated:
            UPDATE_COUNT.inc()  # Incrementa o contador de atualizações
            return request.product

        ERROR_COUNT.inc()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        return product_service_pb2.Product()

    def DeleteProduct(self, request, context):
        product = self.repository.get_product_by_id(request.id)
        if product:
            self.repository.delete_product(request.id)
            DELETE_COUNT.inc()  # Incrementa o contador de eliminações
            return product_service_pb2.StandardResponse(success=True, message="Product deleted")

        ERROR_COUNT.inc()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        return product_service_pb2.StandardResponse(success=False, message="Product not found")

def signal_handler(sig, frame):
    logging.info('Você pressionou Ctrl+C! Encerrando o servidor...')
    server.stop(0)
    sys.exit(0)

def serve():
    start_http_server(8001)  # Inicia o servidor HTTP para Prometheus
    global server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()

    logging.info("Servidor iniciado. Ouvindo na porta 3002.")

    signal.signal(signal.SIGINT, signal_handler)

    try:
       server.wait_for_termination()
    except KeyboardInterrupt:
       logging.info("Interrupção de teclado recebida. Encerrando o servidor...")
       server.stop(0)

if __name__ == '__main__':
   serve()

