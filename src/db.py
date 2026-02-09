import os
import asyncpg

class Database:
    pool = None
    @staticmethod
    async def init():
        print('HI from database')
        Database.pool = await asyncpg.create_pool(
            host=os.getenv("DATABASE_IP"),
            port=5432,
            database="postgres",
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            min_size=1,
            max_size=10,
        )

        if await Database.ping():
            print("Database connected")
            return
        
        print("Failed pining database")
        SystemExit(1)
        

    @staticmethod
    async def ping() -> bool:
        if Database.pool is None:
            raise RuntimeError("Database not initialized")

        async with Database.pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")

        return result == 1