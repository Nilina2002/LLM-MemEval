"""SQLAlchemy repository for conversation messages."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.message import Message, MessageRole
from app.models.message import MessageModel


class SQLMessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, message: Message) -> Message:
        model = self._to_model(message)
        self._session.add(model)
        await self._session.flush()
        return message

    async def create_many(self, messages: list[Message]) -> list[Message]:
        models = [self._to_model(m) for m in messages]
        self._session.add_all(models)
        await self._session.flush()
        return messages

    async def get_by_experiment(
        self,
        experiment_id: str,
        limit: int = 500,
        offset: int = 0,
    ) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.experiment_id == experiment_id)
            .order_by(MessageModel.turn_number, MessageModel.role)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    async def count_by_experiment(self, experiment_id: str) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).where(MessageModel.experiment_id == experiment_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    def _to_model(entity: Message) -> MessageModel:
        return MessageModel(
            id=entity.id,
            experiment_id=entity.experiment_id,
            turn_number=entity.turn_number,
            role=entity.role.value,
            content=entity.content,
            tokens=entity.tokens,
            timestamp=entity.timestamp,
            contains_injected_fact=entity.contains_injected_fact,
            fact_id=entity.fact_id,
            latency_ms=entity.latency_ms,
            cost_usd=entity.cost_usd,
        )

    @staticmethod
    def _to_entity(model: MessageModel) -> Message:
        return Message(
            id=model.id,
            experiment_id=model.experiment_id,
            turn_number=model.turn_number,
            role=MessageRole(model.role),
            content=model.content,
            tokens=model.tokens,
            timestamp=model.timestamp,
            contains_injected_fact=model.contains_injected_fact,
            fact_id=model.fact_id,
            latency_ms=model.latency_ms,
            cost_usd=model.cost_usd,
        )
