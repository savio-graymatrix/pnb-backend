from beanie import Document, Link
from pydantic import Field
from datetime import datetime, timezone
from .Product import Product
from .Customer import Customer


class ProductPurchaseLink(Document):
    product: Link[Product]
    customer: Link[Customer]
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
