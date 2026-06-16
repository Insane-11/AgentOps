from math import ceil

from fastapi import Query
from pydantic import BaseModel


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    total_pages: int


def paginate(items: list, total: int, params: PaginationParams) -> dict:
    return {
        "items": items,
        "total": total,
        "page": params.page,
        "per_page": params.per_page,
        "total_pages": ceil(total / params.per_page) if params.per_page else 0,
    }
