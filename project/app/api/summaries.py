from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path

from app.api import crud
from app.models.tortoise import SummarySchema
from app.summarizer import generate_summary

from app.models.pydantic import (  # isort:skip
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummaryUpdatePayloadSchema,
)

router = APIRouter()


@router.post(
    "/", response_model=SummaryResponseSchema, status_code=201, tags=["summaries"]
)
async def create_summary(
    payload: SummaryPayloadSchema, background_tasks: BackgroundTasks
) -> SummaryResponseSchema:
    summary_id = await crud.post(payload)

    background_tasks.add_task(generate_summary, summary_id, payload.url)

    response_object = {"id": summary_id, "url": payload.url}
    return response_object


@router.get("/", response_model=List[SummarySchema], tags=["summaries"])
async def read_all_summaries() -> List[SummarySchema]:
    return await crud.get_all()


@router.get("/{id}/", response_model=SummarySchema, tags=["summaries"])
async def read_summary(id: int = Path(..., gt=0)) -> SummarySchema:
    summary = await crud.get(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    return summary


@router.delete("/{id}/", response_model=SummaryResponseSchema, tags=["summaries"])
async def delete_summary(id: int = Path(..., gt=0)) -> SummaryResponseSchema:
    summary = await crud.get(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    await crud.delete(id)

    return summary


@router.put("/{id}/", response_model=SummarySchema, tags=["summaries"])
async def update_summary(
    *, id: int = Path(..., gt=0), payload: SummaryUpdatePayloadSchema
) -> SummarySchema:
    summary = await crud.put(id, payload)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    return summary
