import grpc
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
import time
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)

class ProductServicer(product_service_pb2_grpc.ProductServiceServicer):
    def __init__(self):
        self.products = []
        self.start_time = time.time()
        logging.info("ProductServicer initialized")

    def GetHealth(self, request, context):
        uptime = time.time() - self.start_time
        version = "1.0.0"  # ou qualquer versão 
        return product_service_pb2.HealthCheckResponse(
            status=f"ok - Uptime: {uptime:.2f} seconds",
            version=version
        )

    def GetProducts(self, request, context):
        logging.info(f"GetProducts requested. Returning {len(self.products)} products")
        return product_service_pb2.GetProductsResponse(products=self.products)
    
    def GetProductById(self, request, context):
        product = next((p for p in self.products if p.id == request.id), None)
        if product:
            return product
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
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        return product_service_pb2.Product()
    
    def DeleteProduct(self, request, context):
        product = next((p for p in self.products if p.id == request.id), None)
        if product:
            self.products.remove(product)
            return product_service_pb2.StandardResponse(success=True, message="Product deleted")
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Product not found")
        return product_service_pb2.StandardResponse(success=False, message="Product not found")

def signal_handler(sig, frame):
    logging.info('Você pressionou Ctrl+C! Encerrando o servidor...')
    server.stop(0)
    sys.exit(0)

def serve():
    global server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_service_pb2_grpc.add_ProductServiceServicer_to_server(ProductServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Servidor iniciado. Ouvindo na porta 50051.")
    
    # Registrar o manipulador de sinal
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("Interrupção de teclado recebida. Encerrando o servidor...")
        server.stop(0)

if __name__ == '__main__':
    serve()