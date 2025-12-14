from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId
from datetime import datetime

# --- Shared Models ---

class RichMediaLink(BaseModel):
    type: str
    url: str

# --- Response Models ---

class CollegeMatch(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    acceptanceRate: str = Field(..., alias="acceptance_rate")
    tuition: str
    emotionalTagline: str = Field(..., alias="emotional_tagline")
    fitReason: Optional[str] = Field(None, alias="default_fit_reason")
    fitReasonStudent: Optional[str] = Field(None, alias="default_fit_reason_student")
    richMediaLinks: List[RichMediaLink] = Field(..., alias="rich_media_links")

    class Config:
        populate_by_name = True
        from_attributes = True

class SoulScanProfile(BaseModel):
    identity_traits: List[str] = []
    learning_style: List[str] = []
    motivations: List[str] = []
    career_vibes: List[str] = []

class SupportCircle(BaseModel):
    peer_progress_stats: str
    leaderboard_glimpse: List[str]
    parent_board_preview: str
    student_board_preview: str

class FamilyHQData(BaseModel):
    monthlyFocus: List[str]
    soulScanProfile: SoulScanProfile
    supportCircle: SupportCircle
    insiderTips: List[str]

# --- Chat Schemas ---

class ChatMessageCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class ChatMessageResponse(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    sender_role: str
    content: str
    timestamp: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True

# --- Auth & User Schemas ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    profile: Optional[Dict[str, Any]] = {}

class UserLogin(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class InviteRequest(BaseModel):
    pass

class InviteResponse(BaseModel):
    invite_token: str

class StudentSignup(UserBase):
    password: str
    invite_token: str
    profile: Optional[Dict[str, Any]] = {}

class UserResponse(UserBase):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    role: str
    is_verified: bool
    family_id: Optional[PydanticObjectId] = None
    profile: Optional[Dict[str, Any]] = {}

    class Config:
        populate_by_name = True
        from_attributes = True