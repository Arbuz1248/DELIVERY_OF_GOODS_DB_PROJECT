import datetime
import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Создание объекта FastAPI
app = FastAPI()

# Настройка базы данных MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://isp_is_Smirnov:12345@192.168.25.23/isp_is_Smirnov"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение модели SQLAlchemy для пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)  # Указываем длину для VARCHAR
    email = Column(String(100), unique=True, index=True)  # Указываем длину для VARCHAR

class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(50), index=True)
    cost = Column(Integer, index=True)

class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    name_customer = Column(String(50), nullable=False, index=True)
    address_customer = Column(String(50), nullable=False, index=True)
    phone_customer = Column(String(12), nullable=False, index=True)
    constract_number = Column(Integer, nullable=False, index=True)
    date_order = Column(Date, index=True, nullable=False)
    name_product = Column(String(50), nullable=False, index=True)
    scheduled_delivery = Column(String(50), nullable=False, index=True)

class Shipments(Base):
    __tablename__ = "shipments"

    id = Column(Integer, nullable=False, index=True, primary_key=True)
    products_id = Column(Integer, ForeignKey("products.id"), index=True)
    date_shipment = Column(Date, index=True, nullable=False)
    have_been_shiped = Column(String(25), nullable=False, index=True)


# Создание таблиц в базе данных (закоментирована чтобы не пересоздавать таблицы каждый раз)
Base.metadata.create_all(bind=engine)

# Определение Pydantic модели для пользователя
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class ProductsCreate(BaseModel):
    product_name: str
    cost: int

class ProductsResponse(BaseModel):
    id: int
    product_name: str
    cost: int

    class Config:
        orm_mode = True

class ShipmentsCreate(BaseModel):
    product_id: int
    date_shipment: datetime.date
    have_been_shiped: str 
        

class ShipmentsResponse(BaseModel):
    id: int
    product_id: int
    date_shipment: datetime.date
    have_been_shiped: str 

    class Config:
        orm_mode = True

class OrdersCreate(BaseModel):
    name_customer: str
    address_customer: str
    phone_customer: str
    constract_number: int
    date_order: datetime.date
    name_product: str
    scheduled_delivery: str

class OrdersResponse(BaseModel):
    id: int
    name_customer: str
    address_customer: str
    phone_customer: str
    constract_number: int
    date_order: datetime.date
    name_product: str
    scheduled_delivery: str

    class Config:
        orm_mode = True

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для получения пользователя по ID
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Маршрут для создания нового пользователя
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

# Products
@app.get("/products/{products_id}", response_model=ProductsResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products/", response_model=ProductsResponse)
def create_product(product: ProductsCreate, db: Session = Depends(get_db)):
    db_product = Products(product_name=product.product_name, cost=product.cost)
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Product is already existed")

@app.delete("/products/{product_id}", response_model=ProductsResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    else:
        db.delete(product)
        db.commit()
        return product

@app.put("/products/{product_id}", response_model=ProductsResponse)
def update_product(product_id: int, product: ProductsCreate, db: Session = Depends(get_db)):
    db_product = Products(product_name=product.product_name,  cost=product.cost)
    current_product = db.query(Products).filter(Products.id == product_id).first()
    if current_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    else:
        current_product.product_name = db_product.product_name
        current_product.cost = db_product.cost
        db.add(current_product)
        db.commit()
        db.refresh(current_product)
    return current_product

# ORDERS
@app.get("/orders/{order_id}", response_model=OrdersResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Orders).filter(Orders.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders/", response_model=OrdersResponse)
def create_order(order: OrdersCreate, db: Session = Depends(get_db)):
    db_order = Orders(name_customer=order.name_customer, address_customer=order.address_customer, phone_customer=order.phone_customer, constract_number=order.constract_number,
                      date_order=order.date_order, name_product=order.name_product, scheduled_delivery=order.scheduled_delivery)
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Order is already existed")
    

