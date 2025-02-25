class ProductNotFoundError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with ID '{product_id}' not found")

class InsufficientStockError(Exception):
    def __init__(self, product_id: int, available: int):
        self.product_id = product_id
        self.available = available
        super().__init__(f"Not enough stock for product {product_id}. Available: {available}")

class UnauthorizedOrderAccessError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Not authorized to access order {order_id}")

class OrderNotFoundError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Order with ID '{order_id}' not found")