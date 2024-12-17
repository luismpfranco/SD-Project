<template>
  <TopNav :cartItemCount="cartItemCount" />
  <router-view
    :products="products"
    :cartItems="cartItems"
    @addToCart="addToCart"
    @removeFromCart="removeFromCart"
    @submitOrder="submitOrder"
  ></router-view>
</template>

<script>
import TopNav from "./components/TopNav.vue";

export default {
  name: "App",
  components: {
    TopNav,
  },
  data() {
    return {
      cartItems: [],
      products: [],
    };
  },
  computed: {
    cartItemCount() {
      return this.cartItems.reduce((total, item) => total + item.quantity, 0);
    },
  },
  mounted() {
    this.getProducts();
  },
  methods: {
    getProducts() {
      fetch("/products.json")
        .then((response) => {
          if (!response.ok) throw new Error("Failed to load products");
          return response.json();
        })
        .then((products) => {
          console.log("Products loaded successfully:", products);
          this.products = products;
        })
        .catch((error) => {
          console.error("Error fetching products:", error);
          alert("Error occurred while fetching products");
        });
    },
    addToCart({ productId, quantity }) {
      const existingCartItem = this.cartItems.find(
        (item) => item.product.id === productId
      );
      if (existingCartItem) {
        existingCartItem.quantity += quantity;
      } else {
        const product = this.products.find(
          (product) => product.id === productId
        );
        if (product) {
          this.cartItems.push({ product, quantity });
        }
      }
    },
    removeFromCart(index) {
      this.cartItems.splice(index, 1);
    },
    submitOrder() {
      const order = {
        customerId: Math.floor(Math.random() * 10000000000).toString(),
        items: this.cartItems.map((item) => ({
          productId: item.product.id,
          quantity: item.quantity,
          price: item.product.price,
        })),
      };

      console.log("Order:", JSON.stringify(order));

      fetch(`/order`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(order),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Order submission failed");
          }
          this.cartItems = [];
          alert("Order submitted successfully");
        })
        .catch((error) => {
          console.error("Error submitting order:", error);
          alert("Error occurred while submitting order");
        });
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 120px;
}

footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #333;
  color: #fff;
  padding: 1rem;
  margin: 0;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

li {
  margin: 0 1rem;
}

a {
  color: #fff;
  text-decoration: none;
}

button {
  padding: 10px;
  background-color: #005f8b;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  height: 42px;
}

.product-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.product-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  margin: 1rem;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
}

.product-card img {
  max-width: 100%;
  margin-bottom: 1rem;
}

.product-card a {
  text-decoration: none;
  color: #333;
}

.product-card h2 {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.product-card p {
  margin-bottom: 1rem;
}

.product-controls {
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
}

.product-controls p {
  margin-right: 20px;
}

.product-controls button:hover {
  background-color: #005f8b;
}

.product-price {
  font-weight: bold;
  font-size: 1.2rem;
}

.quantity-input {
  width: 50px;
  height: 30px;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 5px;
  margin-right: 10px;
}

.shopping-cart {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.shopping-cart h2 {
  font-size: 24px;
  margin-bottom: 20px;
}

.shopping-cart-table {
  width: 100%;
  border-collapse: collapse;
}

.shopping-cart-table th,
.shopping-cart-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.shopping-cart-table th {
  font-weight: bold;
}

.shopping-cart-table td img {
  display: block;
  margin: 0 auto;
}

.checkout-button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #007acc;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.checkout-button:hover {
  background-color: #005f8b;
}
</style>
