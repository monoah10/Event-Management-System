from fastapi import APIRouter, Depends, HTTPException, Response
from backend.database import SessionLocal
from backend.models import User
from backend.schemas import UserCreate, UserResponse, LoginRequest, UserRole, UserUpdate
from backend.auth import authenticate_user, create_access_token, get_current_user, hash_password, is_admin

router = APIRouter(prefix="/users", tags=["Users Management"])

@router.post("/register", summary="Register a new user", response_model=UserResponse)
async def register(user: UserCreate):
    """
    Register a new user with a role of 'admin', 'organizer', or 'attendee'.
    """
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("", summary="List all attendee", response_model=list[UserResponse])
async def list_users():
    """
    Retrieve a list of all attendee.
    """
    db = SessionLocal()
    users = db.query(User).all()
    user = [user for user in users if user.role not in ["admin", "organizer"]]
    return user

@router.post("/login", summary="User login with JWT")
async def login(login_data: LoginRequest, response: Response):
    """
    Login user using username and password.
    Returns JWT token on success.
    """
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": user.id})
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", summary="Get current user info", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """
    Retrieve the details of the currently authenticated user.
    """
    return user


@router.delete("/{user_id}/delete", summary="Delete a user (Admin only)")
def delete_user(user_id: int, admin=Depends(is_admin)):
    """
    Allows an admin to delete a user by their ID.
    """
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/all_users", summary="Get all users (Admin only)", response_model=list[UserResponse])
def get_all_users(admin=Depends(is_admin)):
    """
    Allows an admin to view all registered users in the system.
    """
    db = SessionLocal()
    users = db.query(User).all()
    return users


@router.put("/{user_id}/update", summary="Update user profile (self or admin)")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user=Depends(get_current_user)
):
    """
    Allows a user to update their own profile or an admin to update any user.
    - Regular users can update their own username.
    - Only admins can change the role to 'attendee' or 'organizer'.
    """
    allowed_roles = ["attendee", "organizer"]
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_admin_user = current_user.role == "admin"
    is_self = current_user.id == user_id

    if not is_admin_user and not is_self:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    if user_update.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = user_update.username

    if user_update.role:
        if is_admin_user:
            if user_update.role not in allowed_roles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Role must be one of: {', '.join(allowed_roles)}"
                )
            user.role = user_update.role
        else:
            raise HTTPException(status_code=403, detail="Only admins can change roles")

    db.commit()
    db.refresh(user)
    return {"message": "User Update successfully", "data": user}

