import logging
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from application.dtos import UserCreateDTO, UserDTO, TokenDTO, UserLoginDTO
from application.use_cases.user_management import RegisterUserUseCase, AuthenticateUserUseCase
from .dependencies import get_register_user_use_case, get_authenticate_user_use_case
from .security import create_access_token

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/token", response_model=TokenDTO)
async def login_for_access_token(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    authenticate_user_use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case)
):
    logger.info(f"Login attempt for username/email: {username} from {request.client.host}")
    
    # Log form data for debugging
    form_data = await request.form()
    logger.debug(f"Form data: {dict(form_data)}")
    
    try:
        login_data = UserLoginDTO(email=username, password=password)
        logger.info(f"Created login DTO for email: {login_data.email}")
        
        user = await authenticate_user_use_case.execute(login_data)
        if not user:
            logger.warning(f"Authentication failed for email: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Invalid credentials",
                    "message": "The email or password you entered is incorrect. Please try again."
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        logger.info(f"User authenticated successfully: {user.email}")
        
        try:
            access_token = create_access_token(
                data={"sub": user.email, "tenant_id": str(user.tenant_id)}
            )
            logger.info("Access token generated successfully")
            return {"access_token": access_token, "token_type": "bearer"}
        except Exception as token_error:
            logger.error(f"Error generating access token: {str(token_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "server_error",
                    "message": "An error occurred while generating authentication token"
                }
            )
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as they are
        raise http_exc
        
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "server_error",
                "message": "An unexpected error occurred during login"
            }
        )


@router.post("/register", response_model=UserDTO)
async def register_user(
    request: Request,
    user_data: UserCreateDTO,
    register_user_use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    """
    Register a new user and tenant.
    
    Requirements:
    - Username must be unique
    - Email must be in a valid format and unique
    - Password must be at least 8 characters long
    - Tenant domain must be unique and URL-friendly (lowercase, alphanumeric with hyphens)
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Registration attempt for email: {user_data.email} from {request.client.host}")
    
    try:
        logger.info(f"Attempting to register user: {user_data.email} with tenant: {user_data.tenant_domain}")
        user = await register_user_use_case.execute(user_data)
        logger.info(f"Successfully registered user: {user.email} with ID: {user.id}")
        return user
        
    except ValueError as e:
        # Handle validation errors
        error_msg = str(e)
        logger.warning(f"Validation error during registration: {error_msg}")
        
        if "email" in error_msg.lower() and "already exists" in error_msg.lower():
            error_msg = "This email is already registered. Please use a different email or log in instead."
        elif "username" in error_msg.lower() and "already exists" in error_msg.lower():
            error_msg = "This username is already taken. Please choose a different username."
        elif "password" in error_msg.lower():
            error_msg = "Password must be at least 8 characters long and contain both letters and numbers."
        
        logger.warning(f"Returning 400 error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
        
    except HTTPException as http_exc:
        logger.warning(f"HTTPException during registration: {str(http_exc)}")
        raise http_exc
        
    except Exception as e:
        error_msg = str(e).lower()
        logger = logging.getLogger(__name__)  # Ensure logger is defined
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        
        # Handle duplicate tenant domain
        if "duplicate key" in error_msg and "tenants_domain_key" in error_msg:
            domain = user_data.tenant_domain
            error_msg = f"The domain '{domain}' is already in use. Please choose a different domain name for your organization."
            logger.warning(f"Domain already in use: {domain}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
            
        # Handle database connection issues
        if "connection" in error_msg or "timeout" in error_msg:
            logger.error("Database connection error during registration", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "database_error",
                    "message": "We're having trouble connecting to our database. Please try again in a few minutes."
                }
            )
            
        # For all other errors, return a generic error message
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "server_error",
                "message": "We encountered an issue while processing your registration. Our team has been notified. Please try again later."
            }
        )
