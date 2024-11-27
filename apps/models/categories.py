from sqlalchemy import VARCHAR, BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from apps.models.database import CreatedBaseModel


class Category(CreatedBaseModel):
    name: Mapped[str] = mapped_column(VARCHAR(255))
    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('categories.id', ondelete='CASCADE'), nullable=True)
    parent: Mapped['Category'] = relationship('Category', lazy='selectin', remote_side='Category.id',
                                              back_populates='subcategories')
    products: Mapped[list['Product']] = relationship('Product', lazy='selectin', back_populates='category')
    subcategories: Mapped[list['Category']] = relationship('Category', lazy='selectin', back_populates='parent')

    def __str__(self):
        if self.parent is None:
            return self.name
        return f"{self.parent} -> {self.name}"

    @classmethod
    async def generate(cls, count: int = 1):
        f = await super().generate(count)
        for _ in range(count):
            await cls.create(
                name=f.company()
            )

    # async def async_product_count(self):
    #     query = select(func.count()).select_from(Product).filter(Product.category_id == self.id)
    #     return (await db.execute(query)).scalar()

    # @property
    # def get_products(self):
    #     # Check if there is an active event loop
    #     if asyncio.get_event_loop().is_running():
    #         # If running in an event loop, create a task
    #         return asyncio.run_coroutine_threadsafe(self.async_product_count(), asyncio.get_event_loop()).result()
    #     else:
    #         # If not running in an event loop, use asyncio.run()
    #         async def inner():
    #             return await self.async_product_count()
    #
    #         return self.run_async(inner)
