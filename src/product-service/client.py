import grpc
import product_service_pb2
import product_service_pb2_grpc
import random

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

    # Listar produtos
    print("\nGetting List of Products:")
    try:
        products_response = client.GetProducts(product_service_pb2.GetProductsRequest())
        products = products_response.products
        for product in products:
            print(f"Product ID: {product.id}, Name: {product.name}, Price: {product.price}")
    except grpc.RpcError as e:
        print(f"Get Products Failed: {e}")
        return  # Sair se não conseguir obter a lista de produtos

    if not products:
        print("No products available.")
        return

    # Criar um conjunto de IDs ocupados
    occupied_ids = {p.id for p in products}

    # Encontrar o menor ID não utilizado
    new_product_id = 1
    while new_product_id in occupied_ids:
        new_product_id += 1

    # Adicionar um produto com ID único
    print("\nAdding a Product:")
    try:
        new_product = product_service_pb2.Product(
            id=new_product_id,  # Garantir ID único
            name=f"New Laptop {random.randint(1, 1000)}",
            price=random.uniform(500, 2000),
            description="A powerful new laptop",
            image="new_laptop.jpg"
        )
        add_response = client.AddProduct(product_service_pb2.AddProductRequest(product=new_product))
        print(f"Add Product Response: {add_response.message}")
    except grpc.RpcError as e:
        print(f"Add Product Failed: {e}")

    # Selecionar produtos aleatórios para atualização e exclusão
    update_product = random.choice(products)
    delete_product = random.choice([p for p in products if p.id != update_product.id])

    # Obter produto por ID para atualização
    print("\nGetting Random Product by ID for Update:")
    try:
        product_response = client.GetProductById(product_service_pb2.GetProductByIdRequest(id=update_product.id))
        print(f"Product ID: {product_response.id}, Name: {product_response.name}, Price: {product_response.price}")
    except grpc.RpcError as e:
        print(f"Get Product By ID Failed: {e}")

    # Atualizar produto
    print("\nUpdating Random Product:")
    try:
        updated_product = product_service_pb2.Product(
            id=update_product.id,
            name=f"Updated {update_product.name}",
            price=update_product.price * 1.1,
            description=f"Updated version of {update_product.name}",
            image=f"updated_{update_product.image}"
        )
        update_response = client.UpdateProduct(product_service_pb2.UpdateProductRequest(product=updated_product))
        print(f"Updated Product ID: {update_response.id}, Name: {update_response.name}, Price: {update_response.price}")
    except grpc.RpcError as e:
        print(f"Update Product Failed: {e}")

    # Eliminar produto
    print("\nDeleting Random Product:")
    try:
        delete_response = client.DeleteProduct(product_service_pb2.DeleteProductRequest(id=delete_product.id))
        print(f"Delete Product Response: {delete_response.message}")
    except grpc.RpcError as e:
        print(f"Delete Product Failed: {e}")

if __name__ == "__main__":
    main()
