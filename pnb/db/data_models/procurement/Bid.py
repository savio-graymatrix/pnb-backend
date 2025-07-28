from datetime import datetime, timezone
from pnb.db.utils.events import create_identifier
from pnb.db.data_models import File
from beanie import Document, before_event, Insert
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal, List

class Bid(Document):
    pass

class UpdateBid(Bid):
    pass