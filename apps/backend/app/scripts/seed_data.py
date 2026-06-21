import asyncio
import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def seed_data():
    """
    Populates the database with initial seed data for restaurants, tables,
    and menus.
    """
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        print("Seeding data...")

        # Seed Restaurant
        await conn.execute(
            text(
                """
            INSERT INTO restaurants (name, code, business_hours, settings)
            VALUES
            ('The Gilded Spoon', 'GDSPN',
            '{"monday": {"open": "11:00", "close": "22:00", "closed": false}, "tuesday": {"open": "11:00", "close": "22:00", "closed": false}}', # noqa: E501
            '{"tableTurnoverTime": 3600, "maxOrdersPerHour": 100, "paymentMethods": ["credit_card", "cash"], "whatsappNotifications": true}') # noqa: E501
            ON CONFLICT (code) DO NOTHING;
        """
            )
        )
        result = await conn.execute(
            text("SELECT id FROM restaurants WHERE code = 'GDSPN'")
        )
        restaurant_id = result.scalar_one_or_none()

        if restaurant_id:
            print(f"Restaurant 'The Gilded Spoon' seeded: ID {restaurant_id}")

            # Seed Tables for the restaurant
            await conn.execute(
                text(
                    """
                INSERT INTO tables (
                    restaurant_id, table_number, capacity, status
                )
                VALUES
                (:res_id, '1A', 4, 'available'),
                (:res_id, '2B', 2, 'occupied'),
                (:res_id, '3C', 6, 'reserved');
            """
                ),
                {"res_id": restaurant_id},
            )
            print("Tables seeded.")

            # Seed Menu for the restaurant
            menu_categories = [
                {
                    "id": "cat-1",
                    "name": "Appetizers",
                    "displayOrder": 1,
                    "items": [
                        {
                            "id": "item-1",
                            "name": "Bruschetta",
                            "price": 8.99,
                            "isAvailable": True,
                            "dietaryInfo": ["vegetarian"],
                        },
                        {
                            "id": "item-2",
                            "name": "Calamari",
                            "price": 12.50,
                            "isAvailable": True,
                            "dietaryInfo": [],
                        },
                    ],
                },
                {
                    "id": "cat-2",
                    "name": "Main Courses",
                    "displayOrder": 2,
                    "items": [
                        {
                            "id": "item-3",
                            "name": "Spaghetti Carbonara",
                            "price": 15.00,
                            "isAvailable": True,
                            "dietaryInfo": [],
                        },
                        {
                            "id": "item-4",
                            "name": "Margherita Pizza",
                            "price": 13.00,
                            "isAvailable": False,
                            "dietaryInfo": ["vegetarian"],
                        },
                    ],
                },
            ]
            await conn.execute(
                text(
                    """
                INSERT INTO menus (
                    restaurant_id, categories, version, is_active
                )
                VALUES (:res_id, :categories, '1.0', true);
            """
                ),
                {
                    "res_id": restaurant_id,
                    "categories": json.dumps(menu_categories),
                },
            )
            print("Menu seeded.")

        else:
            print(
                "Restaurant 'gilded-spoon' already exists or failed to create,"
                " skipping dependent data."
            )

        print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed_data())
