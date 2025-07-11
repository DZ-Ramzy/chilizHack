from pydantic import BaseModel, Field
from typing import List, Optional


class UserRegistrationRequest(BaseModel):
    address: str = Field(..., description="User's blockchain wallet address")
    favorite_teams: Optional[List[str]] = Field(default_factory=list)


class UserResponse(BaseModel):
    address: str
    favorite_teams: List[str] = []
    registered: bool = True

    class Config:
        from_attributes = True 