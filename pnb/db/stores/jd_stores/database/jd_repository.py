import asyncio
import json
from pnb.db.stores.jd_stores.database.db_connection import get_connection

async def save_jd(role: str, experience: float, skills: list[str], location: list[str], jd_text: str):
    loop = asyncio.get_running_loop()

    def _save():
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO job_descriptions (role, experience, skills, location, jd_text)
        VALUES (%s, %s, %s, %s, %s)
        """
        # Convert lists to JSON before inserting
        cursor.execute(
            query,
            (
                role,
                experience,
                json.dumps(skills),   # ✅ store as JSON string
                json.dumps(location), # ✅ store as JSON string
                jd_text
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "✅ Job description saved successfully!"

    return await loop.run_in_executor(None, _save)
