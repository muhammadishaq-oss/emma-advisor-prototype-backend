from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import secrets
import random
from datetime import datetime

from models import User, Family, College, Milestone, Tip, ChatMessage
from schemas import (
    CollegeMatch, FamilyHQData, SoulScanProfile, SupportCircle,
    UserCreate, UserLogin, Token, InviteResponse, StudentSignup, UserResponse,
    ChatMessageCreate, ChatMessageResponse
)
from auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

# --- Auth Routes ---

@router.post("/auth/signup/parent", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_parent(user_data: UserCreate):
    # Check existing
    if await User.find_one(User.email == user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        # Create User
        new_user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            role="parent",
            is_verified=False,
            profile=user_data.profile
        )
        await new_user.create()

        # Create Family
        new_family = Family(parent_id=new_user.id)
        await new_family.create()

        # Link user to family
        new_user.family_id = new_family.id
        await new_user.save()
        
        return new_user
    except Exception as e:
        # In a real app, log the error
        print(f"Error creating parent account: {e}")
        # Rollback would be good here if transactions were supported fully across all mongo versions/drivers used here easily
        # For prototype, we'll raise server error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create account")

@router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    # Find user
    user = await User.find_one(User.email == login_data.email)
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/invite", response_model=InviteResponse)
async def generate_invite(current_user: User = Depends(get_current_user)):
    if current_user.role != "parent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only parents can generate invites")
    
    if not current_user.family_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a family")

    try:
        # Generate token
        invite_token = secrets.token_urlsafe(16)
        
        # Update Family
        family = await Family.get(current_user.family_id)
        if not family:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
             
        family.invite_token = invite_token
        await family.save()
        
        return {"invite_token": invite_token}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating invite: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate invite")

@router.post("/auth/signup/student", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_student(signup_data: StudentSignup):
    # Validate token
    family = await Family.find_one(Family.invite_token == signup_data.invite_token)
    
    if not family:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invite token")
        
    if family.student_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Family already has a student registered")

    # Check email
    if await User.find_one(User.email == signup_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        # Create Student
        new_student = User(
            email=signup_data.email,
            hashed_password=get_password_hash(signup_data.password),
            role="student",
            is_verified=True,
            family_id=family.id,
            profile=signup_data.profile
        )
        await new_student.create()
        
        # Update Family
        family.student_id = new_student.id
        family.invite_token = None # Invalidate token after use
        await family.save()
        
        return new_student
    except Exception as e:
        print(f"Error creating student account: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create account")


# --- Data Routes ---

@router.get("/api/colleges/matches", response_model=List[CollegeMatch])
async def get_college_matches(current_user: User = Depends(get_current_user)):
    # In a real scenario, we'd filter based on student profile/preferences using embeddings
    # For now, we'll simulate AI matching by returning a random subset of colleges
    # This makes the "matching" feel dynamic for the prototype
    
    all_colleges = await College.find_all().to_list()
    
    # Shuffle and pick 2-3 colleges to simulate a "curated" list
    if len(all_colleges) > 0:
        num_matches = min(len(all_colleges), 3)
        return random.sample(all_colleges, num_matches)
    
    return []

@router.get("/api/dashboard/family", response_model=FamilyHQData)
async def get_family_dashboard_data(current_user: User = Depends(get_current_user)):
    return await _get_dashboard_data()

@router.get("/api/public/dashboard/preview", response_model=FamilyHQData)
async def get_public_dashboard_preview():
    return await _get_dashboard_data()

async def _get_dashboard_data():
    # Fetch milestones
    milestones = await Milestone.find(Milestone.is_default == True).to_list()
    monthly_focus = [m.text for m in milestones]

    # Fetch tips
    tips = await Tip.find_all().to_list()
    insider_tips = [t.text for t in tips]

    # Mock/Profile data for the rest
    student_profile = SoulScanProfile(
        identity_traits=["Curious", "Analytical", "Creative", "Empathetic"],
        learning_style=["Hands-on", "Collaborative", "Self-directed"],
        motivations=["Impact", "Innovation", "Personal Growth"],
        career_vibes=["Research", "Arts & Culture", "Social Impact"]
    )
    
    support_circle = SupportCircle(
        peer_progress_stats="85% of students in your cohort have started their essays.",
        leaderboard_glimpse=["Top Essay Drafts: Alex C., Maya S.", "Most College Visits: Ben T., Chloe L."],
        parent_board_preview="Discussion: 'Navigating financial aid forms.'",
        student_board_preview="Poll: 'What's your biggest college application stress?'"
    )

    return FamilyHQData(
        monthlyFocus=monthly_focus,
        soulScanProfile=student_profile,
        supportCircle=support_circle,
        insiderTips=insider_tips
    )

# --- Chat Routes ---

@router.post("/api/chat", response_model=ChatMessageResponse)
async def send_chat_message(message: ChatMessageCreate, current_user: User = Depends(get_current_user)):
    if not current_user.family_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not linked to a family")

    try:
        # 1. Save User Message
        user_msg = ChatMessage(
            family_id=current_user.family_id,
            sender_id=current_user.id,
            sender_role=current_user.role,
            content=message.content,
            metadata=message.metadata
        )
        await user_msg.create()

        # 2. AI Processing (Stub)
        # This is where LangChain/OpenAI integration would happen
        # For now, a simple echo/response stub
        ai_response_content = f"I'm Emma, your AI advisor. I received your message: '{message.content}'. I'm currently running in stub mode, but I'm ready to be connected to OpenAI!"
        
        ai_msg = ChatMessage(
            family_id=current_user.family_id,
            sender_role="ai",
            content=ai_response_content
        )
        await ai_msg.create()

        return ChatMessageResponse(
            _id=ai_msg.id,
            sender_role=ai_msg.sender_role,
            content=ai_msg.content,
            timestamp=ai_msg.timestamp
        )
    except Exception as e:
        print(f"Error in chat processing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process message")

@router.get("/api/chat/history", response_model=List[ChatMessageResponse])
async def get_chat_history(current_user: User = Depends(get_current_user)):
    if not current_user.family_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not linked to a family")
    
    try:
        messages = await ChatMessage.find(ChatMessage.family_id == current_user.family_id).sort(+ChatMessage.timestamp).to_list()
        return messages
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch chat history")