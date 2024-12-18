import grpc
import product_pb2
import product_pb2_grpc

def test_get_products():
    try:
        channel = grpc.insecure_channel('localhost:3002')
        stub = product_pb2_grpc.ProductServiceStub(channel)
        request = product_pb2.Empty()
        response = stub.GetProducts(request)
        
        for product in response.products:
            print(f"Product ID: {product.id}")
            print(f"Name: {product.name}")
            print(f"Price: ${product.price}")
            print(f"Description: {product.description}")
            print(f"Image URL: {product.image}")
            print("---")
            
    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}, {e.details()}")
    finally:
        channel.close()

if __name__ == '__main__':
    test_get_products()