from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

from fastapi import APIRouter, Depends, File, Query, HTTPException, UploadFile
from api.db import get_session, AsyncSession
from api.auth import kc_service, User
from api.models.domain import Campaign, RewardDocument
from api.models.query import CampaignResult, CampaignDraft, CampaignRead, RewardDocumentRead, RewardDocumentResult
from api.services.campaigns import CampaignService
from enacit4r_sql.utils.query import validate_params, ValidationError

from api.services.rewards import RewardsService


def _to_reward_document_read(reward: RewardDocument) -> RewardDocumentRead:
    return RewardDocumentRead(
        id=reward.id,
        campaign_id=reward.campaign_id,
        name=reward.name,
        content=None,
        size=reward.size,
        token=reward.token,
        created_at=reward.created_at,
        created_by=reward.created_by,
        updated_at=reward.updated_at,
        updated_by=reward.updated_by,
    )


def _iter_pdf_files_from_zip_content(content: bytes) -> list[tuple[str, bytes]]:
    pdf_files: list[tuple[str, bytes]] = []
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir).resolve()
        zip_path = root / "archive.zip"
        zip_path.write_bytes(content)

        with ZipFile(zip_path) as archive:
            for member in archive.infolist():
                target_path = (root / member.filename).resolve()
                if root not in target_path.parents and target_path != root:
                    raise HTTPException(
                        status_code=400, detail="ZIP archive contains invalid paths")
            archive.extractall(root)

        for candidate in root.rglob("*"):
            if not candidate.is_file():
                continue
            if candidate.suffix.lower() != ".pdf":
                continue
            base_name = candidate.name
            pdf_files.append((base_name, candidate.read_bytes()))

    return pdf_files


router = APIRouter()


@router.get("/", response_model=CampaignResult, response_model_exclude_none=True)
async def find(
    filter: str = Query(None),
    select: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info()),
) -> CampaignResult:
    """Search for campaigns"""
    try:
        validated = validate_params(filter, sort, range, select)
        return await CampaignService(session).find(validated["filter"], validated["fields"], validated["sort"], validated["range"], user, special_permissions="read-aggregated")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{id}", response_model=CampaignRead, response_model_exclude_none=True)
async def get(id: int,
              session: AsyncSession = Depends(get_session),
              user: User = Depends(kc_service.get_user_info())
              ) -> Campaign:
    """Get a campaign by id"""
    return await CampaignService(session).get(id, user)


@router.delete("/{id}", response_model=Campaign, response_model_exclude_none=True)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Campaign:
    """Delete a campaign by id"""
    return await CampaignService(session).delete(id, user)


@router.post("/", response_model=Campaign, response_model_exclude_none=True)
async def create(
    item: CampaignDraft,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Campaign:
    """Create a campaign"""
    return await CampaignService(session).create(item, user)


@router.put("/{id}", response_model=Campaign, response_model_exclude_none=True)
async def update(
    id: int,
    item: CampaignDraft,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> Campaign:
    """Update a campaign by id"""
    return await CampaignService(session).update(id, item, user)


@router.get("/{id}/rewards", response_model=RewardDocumentResult, response_model_exclude_none=True)
async def get_rewards_for_campaign(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> RewardDocumentResult:
    """Get all reward documents summary for a campaign"""
    # check campaign exists and user has permissions to view it
    await CampaignService(session).get(id, user)
    rewards = await RewardsService(session).get_reward_documents_for_campaign(id)
    return RewardDocumentResult(total=len(rewards), skip=0, limit=None, data=rewards)


@router.post("/{id}/rewards/_upload", response_model=RewardDocumentResult, response_model_exclude_none=True)
async def upload_reward_document(
    id: int,
    files: list[UploadFile] = File(
        default=[],
        description="One or more PDF files containing participant rewards"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> RewardDocumentResult:
    """Upload reward documents and assign each to the next participant without reward document"""
    # check campaign exists and user has permissions to edit it
    await CampaignService(session).get(id, user)

    all_files = list(files)

    if not all_files:
        raise HTTPException(
            status_code=400, detail="At least one file is required")

    rewards_service = RewardsService(session)
    uploaded_rewards: list[RewardDocumentRead] = []

    for uploaded_file in all_files:
        name = uploaded_file.filename
        if not name:
            raise HTTPException(status_code=400, detail="Filename is required")

        content = await uploaded_file.read()
        if not content:
            raise HTTPException(
                status_code=400, detail=f"File '{name}' is empty")

        lower_name = name.lower()
        documents_to_create: list[tuple[str, bytes]] = []
        if lower_name.endswith(".pdf"):
            documents_to_create.append((name, content))
        elif lower_name.endswith(".zip"):
            try:
                documents_to_create = _iter_pdf_files_from_zip_content(content)
            except BadZipFile:
                raise HTTPException(
                    status_code=400, detail=f"File '{name}' is not a valid ZIP archive")

            if not documents_to_create:
                raise HTTPException(
                    status_code=400, detail=f"ZIP file '{name}' does not contain any PDF")
        else:
            raise HTTPException(
                status_code=400, detail="Only PDF and ZIP files are allowed")

        for document_name, document_content in documents_to_create:
            if not document_content:
                raise HTTPException(
                    status_code=400, detail=f"File '{document_name}' is empty")

            reward = await rewards_service.create_reward_document(id, document_name, document_content, user)
            uploaded_rewards.append(_to_reward_document_read(reward))

    return RewardDocumentResult(
        total=len(uploaded_rewards),
        skip=0,
        limit=None,
        data=uploaded_rewards,
    )
