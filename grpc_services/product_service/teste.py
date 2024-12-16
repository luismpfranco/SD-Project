import pytest
import grpc
from unittest.mock import MagicMock
from product_service import ProductServicer, product_service_pb2

@pytest.fixture
def servicer():
    return ProductServicer()

def test_get_health(servicer):
    request = MagicMock()
    context = MagicMock()
    response = servicer.GetHealth(request, context)
    assert "ok" in response.status
    assert response.version == "1.0.0"

def test_get_products(servicer):
    request = MagicMock()
    context = MagicMock()
    response = servicer.GetProducts(request, context)
    assert isinstance(response, product_service_pb2.GetProductsResponse)

def test_add_product(servicer):
    request = product_service_pb2.AddProductRequest(
        product=product_service_pb2.Product(name="Test Product", price=10.0)
    )
    context = MagicMock()
    response = servicer.AddProduct(request, context)
    assert response.success
    assert "Product added" in response.message
