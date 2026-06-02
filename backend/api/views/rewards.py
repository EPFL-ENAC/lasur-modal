from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.query import RewardDocumentRead
from api.services.rewards import RewardsService
from api.services.campaigns import CampaignService

router = APIRouter()


@router.get("/{id}", response_model=RewardDocumentRead, response_model_exclude_none=True)
async def get_reward_document(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> RewardDocumentRead:
    """Get a reward document by id"""
    reward = await RewardsService(session).get_reward_document(id)
    # check campaign exists and user has permissions to view it
    await CampaignService(session).get(reward.campaign_id, user)
    return reward


@router.get("/{id}/_download")
async def download_reward_document(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> StreamingResponse:
    """Download a reward document by id"""
    reward = await RewardsService(session).get_reward_document(id)
    # check campaign exists and user has permissions to view it
    await CampaignService(session).get(reward.campaign_id, user)

    filename = reward.name if reward.name.lower().endswith(
        ".pdf") else f"{reward.name}.pdf"
    return StreamingResponse(
        BytesIO(reward.content or b""),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.delete("/_bulk")
async def bulk_delete_reward_documents(
    ids: list[int] = Query(...,
                           description="List of reward document ids to delete"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
):
    """Bulk delete reward documents by their ids"""
    campaigns_checked = set()
    for id in ids:
        reward = await RewardsService(session).get_reward_document_summary(id)
        if reward.campaign_id not in campaigns_checked:
            # check campaign exists and user has permissions to delete it
            await CampaignService(session).get(reward.campaign_id, user)
            campaigns_checked.add(reward.campaign_id)
        await RewardsService(session).delete_reward_document(id)


@router.delete("/{id}")
async def delete_reward_document(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
):
    """Delete a reward document by id"""
    reward = await RewardsService(session).get_reward_document_summary(id)
    # check campaign exists and user has permissions to delete it
    await CampaignService(session).get(reward.campaign_id, user)
    await RewardsService(session).delete_reward_document(id)
