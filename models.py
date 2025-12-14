from typing import Optional, Dict, Any, List
from beanie import Document, Indexed, PydanticObjectId
from pydantic import EmailStr, Field, BaseModel
from datetime import datetime

class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    role: str  # "parent" or "student"
    is_verified: bool = False
    profile: Dict[str, Any] = {}
    family_id: Optional[PydanticObjectId] = None

    class Settings:
        name = "users"

class Family(Document):
    parent_id: PydanticObjectId
    student_id: Optional[PydanticObjectId] = None
    invite_token: Optional[Indexed(str, unique=True)] = None

    class Settings:
        name = "families"

class RichMediaLink(BaseModel):
    type: str
    url: str

class College(Document):
    name: Indexed(str, unique=True)
    acceptance_rate: str
    tuition: str
    emotional_tagline: str
    rich_media_links: List[RichMediaLink] = []
    
    # Generic fit reasons that might be used as fallback
    default_fit_reason: Optional[str] = None
    default_fit_reason_student: Optional[str] = None

    class Settings:
        name = "colleges"

class Milestone(Document):
    text: str
    month: Optional[str] = None
    is_default: bool = True
    
    class Settings:
        name = "milestones"

class Tip(Document):
    text: str
    
    class Settings:
        name = "tips"

class ChatMessage(Document):
    family_id: Indexed(PydanticObjectId)
    sender_id: Optional[PydanticObjectId] = None # None for AI
    sender_role: str # "parent", "student", "ai"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {} 

    class Settings:
        name = "chat_messages"