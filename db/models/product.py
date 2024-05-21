from sqlalchemy import BigInteger, VARCHAR, ForeignKey, select, INTEGER, TEXT
from sqlalchemy.orm import mapped_column, Mapped, relationship
from db.base import CreatedModel, db
from db.utils import CustomImageField

class User(CreatedModel):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(VARCHAR(255))
    username: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    phone_number: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    orders: Mapped[list['Order']] = relationship('Order', back_populates='user')

class Category(CreatedModel):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255))
    products: Mapped[list['Product']] = relationship("Product", back_populates="category")

class Product(CreatedModel):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255))
    description: Mapped[str] = mapped_column(TEXT)
    price: Mapped[int] = mapped_column(BigInteger, nullable=True)
    photo: Mapped[str] = mapped_column(CustomImageField)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Category.id, ondelete='CASCADE'))
    category: Mapped[Category] = relationship("Category", back_populates="products")
    orders: Mapped[list['Order']] = relationship("Order", back_populates='product')

    @classmethod
    async def get_products_by_category_id(cls, category_id):
        query = select(cls).where(cls.category_id == category_id)
        return (await db.execute(query)).scalars().all()

class Order(CreatedModel):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id, ondelete='CASCADE'))
    category_id: Mapped[int] = mapped_column(BigInteger)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Product.id, ondelete='CASCADE'))
    quantity: Mapped[int] = mapped_column(INTEGER, nullable=True)
    user: Mapped[User] = relationship("User", back_populates="orders")
    product: Mapped[Product] = relationship("Product", back_populates="orders")
