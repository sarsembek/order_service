import pytest
from sqlalchemy.orm import Session
from app.services.order_service import OrderService
from app.core.schemas.order_schema import OrderCreateSchema
from app.core.models.user import User
from app.core.models.order import OrderStatus
from app.core.models.product import Product
from app.core.exceptions.custom_exceptions import ProductNotFoundError, InsufficientStockError
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository

@pytest.fixture
def db_session():
    # Setup code for creating a test database session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base

    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture
def order_service(db_session: Session):
    repository = OrderRepository(db_session)
    return OrderService(repository=repository, db=db_session)

@pytest.fixture
def product_repository(db_session: Session):
    return ProductRepository(db_session)

@pytest.fixture
def current_user():
    return User(username="testuser", email="test@example.com", is_admin=True)

def test_create_order(order_service: OrderService, product_repository: ProductRepository, current_user: User):
    # Create a product in the test database
    product = Product(name="Test Product", price=100, quantity=10)
    product_repository.create(product)

    order_data = OrderCreateSchema(products=[{"product_id": product.product_id, "quantity": 2}])
    order = order_service.create_order(order_data, current_user)
    assert order.customer_name == "testuser"
    assert order.order_status == OrderStatus.PENDING

def test_create_order_product_not_found(order_service: OrderService, current_user: User):
    order_data = OrderCreateSchema(products=[{"product_id": 999, "quantity": 2}])
    with pytest.raises(ProductNotFoundError):
        order_service.create_order(order_data, current_user)

def test_create_order_insufficient_stock(order_service: OrderService, product_repository: ProductRepository, current_user: User):
    # Create a product in the test database with insufficient stock
    product = Product(name="Test Product", price=100, quantity=1)
    product_repository.create(product)

    order_data = OrderCreateSchema(products=[{"product_id": product.product_id, "quantity": 1000}])
    with pytest.raises(InsufficientStockError):
        order_service.create_order(order_data, current_user)