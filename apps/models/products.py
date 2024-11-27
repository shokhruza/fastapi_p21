from enum import Enum

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from slugify import slugify
from sqlalchemy import BigInteger, Enum as SqlEnum, String, VARCHAR, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy_file import ImageField
from apps.models.categories import Category

from apps.models.database import CreatedBaseModel
from config import storage, get_currency_in_sum


class Product(CreatedBaseModel):
    class Currency(str, Enum):
        UZS = 'uzs'
        USD = 'usd'

    name: Mapped[str] = mapped_column(VARCHAR(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    discount_price: Mapped[int] = mapped_column(Integer, nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(SqlEnum(Currency), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, server_default="0")
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Category.id, ondelete='CASCADE'))
    category: Mapped['Category'] = relationship('Category', lazy='selectin', back_populates='products')
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    owner: Mapped['User'] = relationship('User', lazy='selectin', back_populates='products')

    photos: Mapped[list['ProductPhoto']] = relationship('ProductPhoto', lazy='selectin', back_populates='product')

    __table_args__ = (
        CheckConstraint('price > discount_price'),
    )

    @property
    def price_uzs(self):
        return self.price * 12500

        sum_price, _ = get_currency_in_sum()
        return self.price * sum_price

    @classmethod
    async def create(cls, **kwargs):
        _slug = slugify(kwargs['name'])
        while cls.get(cls.slug == _slug) is not None:
            _slug = slugify(kwargs['name'] + '-1')
        kwargs['slug'] = _slug
        return await super().create(**kwargs)


class ProductPhoto(CreatedBaseModel):
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('products.id', ondelete='CASCADE'))
    product: Mapped['Product'] = relationship('Product', lazy='selectin', back_populates='photos')
    photo: Mapped[ImageField] = mapped_column(ImageType(storage=FileSystemStorage('media/products/')))
