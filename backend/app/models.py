from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(String(36), primary_key=True)
    user_id = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    item_id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(String(36), ForeignKey("receipts.receipt_id"))
    item_name = Column(String(255))
    quantity = Column(Float)
    unit = Column(String(20))
    price = Column(Float)


class Nutrition(Base):
    __tablename__ = "nutrition"

    nutrition_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("receipt_items.item_id"))
    quantity_grams = Column(Float)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)