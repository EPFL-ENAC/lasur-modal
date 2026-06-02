
from fastapi import HTTPException
from datetime import datetime

from sqlalchemy import func
from sqlmodel import select

from api.db import AsyncSession
from api.models.domain import RewardDocument
from api.models.query import RewardDocumentRead
from api.auth import User


class RewardsService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_reward_documents_for_campaign(self, campaign_id: int, assigned: bool | None = None) -> int:
        """Count reward documents for a campaign"""
        statement = select(func.count()).select_from(RewardDocument).where(
            RewardDocument.campaign_id == campaign_id)
        if assigned is True:
            statement = statement.where(RewardDocument.token != None)
        elif assigned is False:
            statement = statement.where(RewardDocument.token == None)

        count = (await self.session.exec(statement)).one()
        return int(count)

    async def get_reward_documents_for_campaign(self, campaign_id: int) -> list[RewardDocumentRead]:
        """Get reward documents for a campaign"""
        res = await self.session.exec(
            select(
                RewardDocument.id,
                RewardDocument.campaign_id,
                RewardDocument.name,
                RewardDocument.size,
                RewardDocument.token,
                RewardDocument.created_at,
                RewardDocument.created_by,
                RewardDocument.updated_at,
                RewardDocument.updated_by,
            ).where(
                RewardDocument.campaign_id == campaign_id))
        return [
            RewardDocumentRead(
                id=document_id,
                campaign_id=document_campaign_id,
                name=document_name,
                content=None,
                size=document_size,
                token=document_token,
                created_at=document_created_at,
                created_by=document_created_by,
                updated_at=document_updated_at,
                updated_by=document_updated_by,
            )
            for (
                document_id,
                document_campaign_id,
                document_name,
                document_size,
                document_token,
                document_created_at,
                document_created_by,
                document_updated_at,
                document_updated_by,
            ) in res.all()
        ]

    async def get_reward_document(self, id: int) -> RewardDocument:
        """Get a reward document by id"""
        res = await self.session.exec(
            select(RewardDocument).where(
                RewardDocument.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Reward document not found")
        return entity

    async def get_reward_document_summary(self, id: int) -> RewardDocumentRead:
        """Get a reward document by id"""
        res = await self.session.exec(
            select(
                RewardDocument.id,
                RewardDocument.campaign_id,
                RewardDocument.name,
                RewardDocument.size,
                RewardDocument.token,
                RewardDocument.created_at,
                RewardDocument.created_by,
                RewardDocument.updated_at,
                RewardDocument.updated_by
            ).where(
                RewardDocument.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Reward document not found")
        return RewardDocumentRead(
            id=entity.id,
            campaign_id=entity.campaign_id,
            name=entity.name,
            content=None,
            size=entity.size,
            token=entity.token,
            created_at=entity.created_at,
            created_by=entity.created_by,
            updated_at=entity.updated_at,
            updated_by=entity.updated_by
        )

    async def delete_reward_document(self, id: int) -> RewardDocument:
        """Delete a reward document by id"""
        res = await self.session.exec(
            select(RewardDocument).where(
                RewardDocument.id == id))
        entity = res.one_or_none()
        if not entity:
            raise HTTPException(
                status_code=404, detail="Reward document not found")
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def create_reward_document(self, campaign_id: int, name: str, content: bytes, user: User = None) -> RewardDocument:
        """Create a reward document for a campaign"""
        entity = RewardDocument(campaign_id=campaign_id,
                                name=name, content=content, size=len(content))
        entity.created_at = datetime.now()
        entity.updated_at = datetime.now()
        if user:
            entity.created_by = user.username
            entity.updated_by = user.username
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_reward_document_for_token(self, token: str, campaign_id: int) -> RewardDocument:
        """Get the next reward document not assigned to any token yet or already assigned to
        the same token. This is used when a participant downloads a reward document with a 
        token.
        """
        # Search if token is not already assigned to a reward document
        res = await self.session.exec(
            select(RewardDocument).where(
                RewardDocument.token == token,
                RewardDocument.campaign_id == campaign_id
            )
        )
        if res.one_or_none() is not None:
            # Return current assigned reward document because document can be downloaded
            # multiple times with the same token until it is assigned to a participant
            return res.one()

        # Get the next reward document not assigned to any token yet
        res = await self.session.exec(
            select(RewardDocument).where(
                RewardDocument.token == None,
                RewardDocument.campaign_id == campaign_id
            ).order_by(RewardDocument.created_at)
        )
        entity = res.first()
        if not entity:
            raise HTTPException(
                status_code=404, detail="No more reward documents available")
        # Assign token to reward document
        entity.token = token
        entity.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(entity)

        # Return assigned reward document
        return entity
