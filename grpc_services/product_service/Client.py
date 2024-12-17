import grpc
import product_service_pb2
import product_service_pb2_grpc

#logging.basicConfig(level=logging.INFO)

def main():
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    client = product_service_pb2_grpc.ProductServiceStub(channel)

    # Testar o HealthCheck
    print("Testing Health Check:")
    try:
        health_response = client.GetHealth(product_service_pb2.GetProductsRequest())
        print(f"Status: {health_response.status}, Version: {health_response.version}")
    except grpc.RpcError as e:
        print(f"Health Check Failed: {e}")

    # Adicionar um produto
    print("\nAdding a Product:")
    try:
        new_product = product_service_pb2.Product(name="Laptop", price=999.99, description="A powerful laptop", image="laptop.jpg")
        add_response = client.AddProduct(product_service_pb2.AddProductRequest(product=new_product))
        print(f"Add Product Response: {add_response.message}")
    except grpc.RpcError as e:
        print(f"Add Product Failed: {e}")

    # Listar produtos
    print("\nGetting List of Products:")
    try:
        products_response = client.GetProducts(product_service_pb2.GetProductsRequest())
        for product in products_response.products:
            print(f"Product ID: {product.id}, Name: {product.name}, Price: {product.price}")
    except grpc.RpcError as e:
        print(f"Get Products Failed: {e}")

    # Obter produto por ID
    print("\nGetting Product by ID:")
    try:
        product_id = 1
        product_response = client.GetProductById(product_service_pb2.GetProductByIdRequest(id=product_id))
        print(f"Product ID: {product_response.id}, Name: {product_response.name}, Price: {product_response.price}")
    except grpc.RpcError as e:
        print(f"Get Product By ID Failed: {e}")

    # Atualizar produto
    print("\nUpdating Product:")
    try:
        updated_product = product_service_pb2.Product(id=1, name="Updated Laptop", price=1099.99, description="An even more powerful laptop", image="updated_laptop.jpg")
        update_response = client.UpdateProduct(product_service_pb2.UpdateProductRequest(product=updated_product))
        print(f"Updated Product ID: {update_response.id}, Name: {update_response.name}, Price: {update_response.price}")
    except grpc.RpcError as e:
        print(f"Update Product Failed: {e}")

    # Eliminar produto
    print("\nDeleting Product:")
    try:
        delete_response = client.DeleteProduct(product_service_pb2.DeleteProductRequest(id=1))
        print(f"Delete Product Response: {delete_response.message}")
    except grpc.RpcError as e:
        print(f"Delete Product Failed: {e}")

if __name__ == "__main__":
    main()