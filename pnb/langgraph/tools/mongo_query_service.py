from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from bson import ObjectId
from pymongo import MongoClient

from pnb import SETTINGS
from pnb.langgraph.tools.mongo_catalog import MongoCatalog

SAFE_OPERATORS = {"$eq", "$gte", "$lte", "$in", "$regex"}
DEFAULT_LIMIT = 25
SORT_MAP = {
    "communications": [("date", -1), ("created_at", -1)],
    "transaction": [("date", -1), ("created_at", -1)],
    "customer": [("updated_at", -1), ("created_at", -1)],
    "lead": [("updated_at", -1), ("created_at", -1)],
    "product": [("updated_at", -1), ("created_at", -1)],
}


@dataclass
class QueryResult:
    rows: List[Dict[str, Any]]
    fields: List[str]
    limit: int
    total_returned: int
    source: str


class DomainQueryService:
    """Validates and executes domain-aware MongoDB queries with redaction and joins."""

    def __init__(self, catalog: MongoCatalog, client: Optional[MongoClient] = None) -> None:
        self._catalog = catalog
        self._client = client or MongoClient(SETTINGS.MONGO_URI)

    def list_collections(self, logical_db: str) -> Dict[str, Any]:
        metadata = self._catalog.describe_database(logical_db)
        return {
            "database": logical_db,
            "collections": metadata["collections"],
        }

    def describe_schema(self, logical_db: str, collection: str) -> Dict[str, Any]:
        schema = self._catalog.get_schema(logical_db, collection)
        return {
            "database": logical_db,
            "collection": schema.collection,
            "fields": schema.fields,
            "relationships": schema.relationships,
        }

    def query(
        self,
        logical_db: str,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        projection: Optional[Iterable[str]] = None,
        limit: int = DEFAULT_LIMIT,
    ) -> QueryResult:
        validated_filters = self._sanitize_filters(filters or {})
        projection_doc = self._build_projection(projection)
        sort = SORT_MAP.get(collection, [("updated_at", -1)])

        db = self._catalog.get_database(logical_db)
        cursor = (
            db[collection]
            .find(validated_filters, projection=projection_doc or None)
            .sort(sort)
            .limit(limit)
        )
        rows = [self._redact(collection, row) for row in cursor]
        fields_out = list(rows[0].keys()) if rows else list(projection_doc.keys() if projection_doc else [])
        return QueryResult(
            rows=rows,
            fields=fields_out,
            limit=limit,
            total_returned=len(rows),
            source=f"{logical_db}.{collection}",
        )

    def customer_overview(
        self,
        name: Optional[str] = None,
        customer_id: Optional[str] = None,
        view: str = "profile",
        limit: int = DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        identifier_filter = self._resolve_customer_identifier(name, customer_id)

        if view == "transactions":
            return self.query(
                logical_db="Transaction",
                collection="transaction",
                filters=identifier_filter,
                limit=limit,
            ).__dict__

        if view == "communications":
            return self.query(
                logical_db="Communication",
                collection="communications",
                filters=identifier_filter,
                limit=limit,
            ).__dict__

        return self.query(
            logical_db="Customer",
            collection="customer",
            filters=identifier_filter,
            limit=limit,
        ).__dict__

    def lead_overview(
        self,
        product_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}
        if product_type:
            filters["product"] = {"$regex": product_type, "$options": "i"}
        if status:
            filters["status"] = {"$regex": status, "$options": "i"}
        return self.query("Lead", "lead", filters=filters, limit=limit).__dict__

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_customer_identifier(
        self, name: Optional[str], customer_id: Optional[str]
    ) -> Dict[str, Any]:
        if customer_id:
            return {"customer_id": customer_id}

        if not name:
            raise ValueError("Either customer name or customer_id must be provided.")

        db = self._catalog.get_database("Customer")
        match = db["customer"].find_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            projection={"customer_id": 1},
        )
        if not match:
            raise ValueError(f"No customer found with name '{name}'.")
        return {"customer_id": match["customer_id"]}

    def _sanitize_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        sanitized: Dict[str, Any] = {}
        for key, value in filters.items():
            if isinstance(value, dict):
                sanitized[key] = {
                    op: val for op, val in value.items() if op in SAFE_OPERATORS
                }
            else:
                sanitized[key] = value
        return sanitized

    def _build_projection(self, projection: Optional[Iterable[str]]) -> Dict[str, int]:
        if not projection:
            return {}
        return {field: 1 for field in projection}

    def _redact(self, collection: str, row: Dict[str, Any]) -> Dict[str, Any]:
        redacted = dict(row)
        mongo_id = redacted.pop("_id", None)
        if mongo_id is not None:
            redacted["document_id"] = str(mongo_id)

        # Remove direct contact details if present
        if "contact" in redacted and isinstance(redacted["contact"], dict):
            redacted["contact"] = {k: "***" for k in redacted["contact"]}
        elif "contact" in redacted:
            redacted["contact"] = "***"

        for key in ("email", "phone", "address"):
            if key in redacted:
                redacted[key] = "***"

        if "customer_id" in redacted and isinstance(redacted["customer_id"], ObjectId):
            redacted["customer_id"] = str(redacted["customer_id"])

        if "product" in redacted and isinstance(redacted["product"], ObjectId):
            redacted["product"] = str(redacted["product"])

        return redacted
