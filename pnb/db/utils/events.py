from datetime import datetime, timezone
from beanie import PydanticObjectId

# Before Insert Event: Create Identifier
async def create_identifier(self):
    if not self.series_id:
        entity = self.__class__.__name__.upper()
        year = datetime.now(timezone.utc).year
        # Count existing users for the year
        year_start = datetime(year, 1, 1)
        year_end = datetime(year + 1, 1, 1)
        count = await self.__class__.find(
            self.__class__.created_at >= year_start,
            self.__class__.created_at < year_end
        ).count()
        serial = str(count + 1).zfill(5)
        self.series_id = f"{entity}-{year}-{serial}"