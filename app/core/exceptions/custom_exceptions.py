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
        
class AuthException(Exception):
    """Base authentication exception"""
    status_code: int = 400

class DuplicateUsernameError(AuthException):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Username '{username}' already exists")
        self.status_code = 409

class InvalidCredentialsError(AuthException):
    def __init__(self):
        super().__init__("Authentication failed")
        self.status_code = 401

class TokenInvalidError(AuthException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail)
        self.status_code = 401

class TokenExpiredError(TokenInvalidError):
    def __init__(self):
        super().__init__("Token has expired")

class InsufficientPermissionsError(AuthException):
    def __init__(self):
        super().__init__("Insufficient permissions")
        self.status_code = 403