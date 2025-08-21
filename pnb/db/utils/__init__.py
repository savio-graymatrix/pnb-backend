from pnb.db.utils.filters import *
from pnb.db.utils.pagination import *
from datetime import datetime, timezone
from beanie import Document
from pnb.db.stores.MongoGraphStore import MONGO_GRAPH_STORE
from langchain_core.documents import Document
from pnb import LOGGER


# Create Identifier
async def create_identifier(self):
    if self.series_id == None:
        entity = self.__class__.__name__.upper()
        year = datetime.now(timezone.utc).year
        # Count existing users for the year
        year_start = datetime(year, 1, 1)
        year_end = datetime(year + 1, 1, 1)
        count = await self.__class__.find(
            self.__class__.created_at >= year_start,
            self.__class__.created_at < year_end,
        ).count()
        serial = str(count + 1).zfill(5)
        self.series_id = f"{entity}-{year}-{serial}"


async def handle_add_to_knowledge_graph(data: Document):
    """ """

    def document_to_text(data: Document):
        return "\n".join(f"{key}: {data}" for key, data in data.model_dump().items())

    document = [Document(page_content=document_to_text(data), metadata={"id": data.id})]
    MONGO_GRAPH_STORE.add_documents(document)
