from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Mapping, Optional

from pymongo import MongoClient
from pymongo.database import Database

from pnb import SETTINGS


@dataclass(frozen=True)
class CollectionSchema:
    collection: str
    fields: Mapping[str, str]
    relationships: Mapping[str, str] = field(default_factory=dict)


SCHEMA_REGISTRY: Mapping[str, List[CollectionSchema]] = {
    "Lead": [
        CollectionSchema(
            collection="lead",
            fields={
                "name": "Lead name",
                "company": "Company name",
                "title": "Role or designation",
                "product": "Interested product (string or Product link)",
                "conversations": "Conversations summary",
                "contact.email": "Email address",
                "contact.phone": "Phone number",
                "status": "Lead lifecycle status",
                "source": "Lead acquisition source",
                "tags": "Lead tags",
                "created_at": "Creation timestamp (UTC)",
                "updated_at": "Last update timestamp (UTC)",
            },
        )
    ],
    "Customer": [
        CollectionSchema(
            collection="customer",
            fields={
                "customer_id": "Business-facing identifier",
                "name": "Customer full name",
                "age": "Age in years",
                "gender": "Gender description",
                "city": "City of residence",
                "occupation": "Occupation category",
                "income": "Annual income",
                "segment": "Customer banking segment",
                "products_held": "List of currently held products",
                "credit_score": "Credit score",
                "preferred_channel": "Preferred communication channel",
                "contacted": "Whether recently contacted",
                "created_at": "Creation timestamp (UTC)",
                "updated_at": "Last update timestamp (UTC)",
                "contact": "Contact details - Phone number",
            },
        )
    ],
    "Communication": [
        CollectionSchema(
            collection="communications",
            fields={
                "comm_id": "Communication identifier",
                "customer_id": "Foreign key to customer.customer_id",
                "date": "Timestamp of interaction",
                "channel": "Interaction channel",
                "intent": "Stated intent of the customer",
                "message": "Customer message body",
                "bank_response": "Bank response content",
                "outcome": "Result of the interaction",
                "created_at": "Record creation timestamp",
            },
            relationships={"customer_id": "Customer.customer_id"},
        )
    ],
    "Transaction": [
        CollectionSchema(
            collection="transaction",
            fields={
                "txn_id": "Transaction identifier",
                "customer_id": "Foreign key to customer.customer_id",
                "date": "Transaction date/time (UTC)",
                "account_type": "Account type",
                "amount": "Transaction amount",
                "channel": "Transaction channel",
                "merchant": "Merchant descriptor",
                "category": "Spending category",
                "balance_after": "Balance after transaction",
                "created_at": "Record creation timestamp",
                "updated_at": "Record update timestamp",
            },
            relationships={"customer_id": "Customer.customer_id"},
        )
    ],
    "Product": [
        CollectionSchema(
            collection="product",
            fields={
                "product_id": "Product identifier",
                "name": "Product name",
                "type": "Product type enum",
                "recommended": "Linked customer segments",
                "description": "Product pitch text",
                "created_at": "Creation timestamp (UTC)",
                "updated_at": "Last update timestamp (UTC)",
            },
        )
    ],
}


class MongoCatalog:
    """Provides catalog metadata and lightweight schema discovery for MongoDB databases."""

    def __init__(self, client: Optional[MongoClient] = None) -> None:
        self._client = client or MongoClient(SETTINGS.MONGO_URI)
        self._db_cache: Dict[str, Database] = {}

    def get_database(self, logical_db: str) -> Database:
        db_map = getattr(SETTINGS, "MONGO_DB_MAP", {})
        db_name = db_map.get(logical_db, SETTINGS.DB_NAME)
        if db_name not in self._db_cache:
            self._db_cache[db_name] = self._client[db_name]
        return self._db_cache[db_name]

    def list_collections(self, logical_db: str) -> Iterable[str]:
        if logical_db in SCHEMA_REGISTRY:
            return [schema.collection for schema in SCHEMA_REGISTRY[logical_db]]
        return self.get_database(logical_db).list_collection_names()

    @lru_cache(maxsize=64)
    def get_schema(self, logical_db: str, collection: str) -> CollectionSchema:
        registry = SCHEMA_REGISTRY.get(logical_db, [])
        for schema in registry:
            if schema.collection == collection:
                return schema

        sampled_schema = self._sample_schema(logical_db, collection)
        fields = {key: "Sampled field" for key in sampled_schema.keys()}
        return CollectionSchema(collection=collection, fields=fields)

    def describe_database(self, logical_db: str) -> Dict[str, Any]:
        return {
            "database": logical_db,
            "collections": [
                {
                    "name": schema.collection,
                    "fields": schema.fields,
                    "relationships": schema.relationships,
                }
                for schema in SCHEMA_REGISTRY.get(logical_db, [])
            ],
        }

    def _sample_schema(self, logical_db: str, collection: str) -> Dict[str, Any]:
        db = self.get_database(logical_db)
        doc = db[collection].find_one()
        return doc or {}
