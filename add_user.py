import asyncio
from collections.abc import Sequence

from sqlalchemy.sql import select

from libs.database.manager import DatabaseManager
from libs.database.model import User
from libs.oauth2 import verify_password

db = DatabaseManager("sqlite+aiosqlite:///data/harmoland-console.db")


async def main():
    await db.initialize()
    # try:
    #     result = await db.add(User(qq=731347477, passwd=get_password_hash('test')))
    #     print('result: ', result)
    # except Exception as e:
    #     print(f'\nError: {e}\n')

    try:
        result: Sequence[User] | None = await db.select_first(select(User).where(User.qq == 731347477))
        print("result: ", result)
        if result is None:
            print("None")
            return
        print(verify_password("test", result[0].passwd))
    except Exception as e:
        print(f"\nError: {e}\n")


asyncio.run(main())
