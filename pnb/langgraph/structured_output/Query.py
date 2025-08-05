from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal


class Query(BaseModel):
    # query: str = Field(description="The query")
    response: str = Field(description="The response by the query agent")