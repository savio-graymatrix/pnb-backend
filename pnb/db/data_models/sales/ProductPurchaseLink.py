from beanie import Document, Link, before_event, after_event, Insert
from pydantic import Field
from datetime import datetime, timezone
from .Product import Product
from .Customer import Customer
from pnb.db.utils import create_identifier, handle_add_to_knowledge_graph
import asyncio


class ProductPurchaseLink(Document):
    product: Link[Product]
    customer: Link[Customer]
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "product_purchase_link"

    @after_event(Insert)
    async def add_to_knowledge_graph(data: Document):
        asyncio.create_task(handle_add_to_knowledge_graph(data=data))

    @before_event(Insert)
    async def handle_indentifier(self):
        await create_identifier(self)
