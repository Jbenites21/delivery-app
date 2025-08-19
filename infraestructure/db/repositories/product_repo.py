from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from config.settings import settings
from infraestructure.db.models import ProductORM
from domain.models.product import Product, ProductCreate

engine= create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product_data: ProductCreate) -> Optional[Product]:
        try:
            db_product = ProductORM(**product_data.model_dump())
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return Product.model_validate(db_product)
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error creating product: {e}")
            raise e
        
    def get_all(self, limit: int, offset: int) -> List[Product]:
        products_orm=self.db.query(ProductORM).limit(limit).offset(offset).all()
        return [Product.model_validate(product) for product in products_orm]