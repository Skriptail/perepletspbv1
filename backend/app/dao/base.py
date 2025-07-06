from sqlalchemy.ext.asyncio import AsyncSession

class BaseDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        """Фиксирует изменения в базе данных."""
        await self.session.commit()

    async def rollback(self):
        """Откатывает изменения в базе данных."""
        await self.session.rollback()
