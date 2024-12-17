import json
import product_service_pb2

class ProductRepository:
    def __init__(self, filename='products.json'):
        self.filename = filename
        self.products = self.load_products()

    def load_products(self):
        try:
            with open(self.filename, 'r') as f:
                return [json.loads(line.strip()) for line in f if line.strip()]
        except FileNotFoundError:
            return []


    def save_products(self):
        with open(self.filename, 'w') as f:
            for product in self.products:
                f.write(json.dumps(product) + '\n')


    def add_product(self, product):
        product_dict = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'image': product.image
        }
        self.products.append(product_dict)
        self.save_products()

    def update_product(self, product):
        for i, p in enumerate(self.products):
            if p['id'] == product.id:
                self.products[i] = {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'description': product.description,
                    'image': product.image
                }
                self.save_products()
                return True
        return False

    def delete_product(self, product_id):
        self.products = [p for p in self.products if p['id'] != product_id]
        self.save_products()

    def get_products(self):
        return self.products

    def get_product_by_id(self, product_id):
        product_dict = next((p for p in self.products if p['id'] == product_id), None)
        if product_dict:
            return product_dict  # Retorna o dicionário diretamente
        return None


