from fastapi import APIRouter, Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import DBSession, CurrentUser
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.userService import UserService

router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(user_in:UserCreate,db:DBSession):
    user_service = UserService(db)
    return  user_service.register_user(user_in)

@router.post("/login", response_model=Token)
def login(db: DBSession,form_data: OAuth2PasswordRequestForm = Depends()):

    user_service = UserService(db)
    login_data = UserLogin(
        email=form_data.username,
        password=form_data.password
    )
    return user_service.authenticate_user(login_data)

@router.post("/logout")
def logout(current_user: CurrentUser):
    return {"message": "Successfully logged out"}