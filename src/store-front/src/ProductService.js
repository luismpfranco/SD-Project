import { ProductServiceClient } from './proto/product_grpc_web_pb';
import { Empty } from './proto/product_pb';

const client = new ProductServiceClient('http://localhost:8080');

export const getProducts = () => {
  return new Promise((resolve, reject) => {
    const request = new Empty();
    
    client.getProducts(request, {}, (err, response) => {
      if (err) {
        console.error('gRPC error:', err);
        reject(err);
        return;
      }
      
      try {
        const products = response.getProductsList();
        if (!products) {
          reject(new Error('No products returned'));
          return;
        }
        resolve(products.map(p => ({
          id: p.getId(),
          name: p.getName(),
          price: p.getPrice(),
          description: p.getDescription(),
          image: p.getImage()
        })));
      } catch (error) {
        console.error('Parse error:', error);
        reject(error);
      }
    });
  });
};