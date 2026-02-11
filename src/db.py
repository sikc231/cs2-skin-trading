import os
from dataclasses import dataclass
import asyncpg

class Cs2Skin:
    def __init__(self, name, price, updated, skin=None, wear=None):
        self.name = name
        self.price = price
        self.updated = updated
        self.skin = skin
        self.wear = wear

class Database:

    @dataclass
    class Cs2Skin:
        name: str
        price: float
        updated: int
        skin: str | None
        wear: str | None
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

    @staticmethod
    async def get_skin_by_market_hash(market_hash: str) -> Cs2Skin | None:
        if Database.pool is None:
            raise RuntimeError("Database not initialized")
        async with Database.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM public.cs2_skins WHERE \"name\" = $1",
                market_hash
            )
            if row:
                return Cs2Skin(
                    name=row["name"],
                    price=float(row["price"]),
                    updated=int(row["updated"]),
                    skin=row["skin"],
                    wear=row["wear"]
                )
            # Insert new row with default values

            print(f"Inserting new skin into database: {market_hash}")
            await conn.execute(
                "INSERT INTO public.cs2_skins (\"name\", price, skin, wear) VALUES ($1, $2, $3, $4)",
                market_hash, 0.0, None, None
            )

        return None