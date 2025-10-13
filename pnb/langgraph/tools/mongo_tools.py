from __future__ import annotations

from typing import Literal, Optional

from langchain_core.tools import tool

from pnb.langgraph.tools.mongo_catalog import MongoCatalog
from pnb.langgraph.tools.mongo_query_service import DomainQueryService

_catalog = MongoCatalog()
_service = DomainQueryService(catalog=_catalog)


@tool("list_mongo_collections")
def list_mongo_collections(
    logical_db: Literal["Lead", "Customer", "Communication", "Transaction", "Product"],
) -> dict:
    """List collections and schema hints for the specified logical database."""

    return _service.list_collections(logical_db)


@tool("describe_mongo_schema")
def describe_mongo_schema(
    logical_db: Literal["Lead", "Customer", "Communication", "Transaction", "Product"],
    collection: str,
) -> dict:
    """Retrieve field descriptions and relationships for a collection."""

    return _service.describe_schema(logical_db, collection)


@tool("query_mongo_collection")
def query_mongo_collection(
    logical_db: Literal["Lead", "Customer", "Communication", "Transaction", "Product"],
    collection: str,
    filters: Optional[dict] = None,
    projection: Optional[list[str]] = None,
    limit: int = 25,
) -> dict:
    """Execute a filtered query against a collection."""

    result = _service.query(
        logical_db=logical_db,
        collection=collection,
        filters=filters,
        projection=projection,
        limit=limit,
    )
    return result.__dict__


@tool("query_customer_view")
def query_customer_view(
    name: Optional[str] = None,
    customer_id: Optional[str] = None,
    view: Literal["profile", "transactions", "communications"] = "profile",
    limit: int = 25,
) -> dict:
    """Retrieve customer profile, transaction, or communication data."""

    return _service.customer_overview(
        name=name,
        customer_id=customer_id,
        view=view,
        limit=limit,
    )


@tool("query_lead_pipeline")
def query_lead_pipeline(
    name: Optional[str] = None,
    product_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
) -> dict:
    """Retrieve leads filtered by product interest and/or status."""

    return _service.lead_overview(
        name=name,
        product_type=product_type,
        status=status,
        limit=limit,
    )
