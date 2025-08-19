import logging
from domain.entities import User, Tenant
from domain.repositories import UserRepository, TenantRepository
from application.services import PasswordService
from application.dtos import UserCreateDTO, UserDTO, UserLoginDTO

logger = logging.getLogger(__name__)

class AuthenticateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_login_dto: UserLoginDTO) -> User | None:
        try:
            logger.info(f"Starting authentication for email: {user_login_dto.email}")
            
            # First try to find user by email
            user = await self.user_repository.get_by_email(user_login_dto.email)
            if not user:
                logger.warning(f"Login attempt failed: No user found with email {user_login_dto.email}")
                return None
            
            logger.info(f"User found: {user.email}, checking password...")
            
            # Verify the password
            is_password_valid = PasswordService.verify_password(user_login_dto.password, user.hashed_password)
            if not is_password_valid:
                logger.warning(f"Login attempt failed: Invalid password for user {user.email}")
                return None
                
            logger.info(f"Password verified for user: {user.email}")
            logger.info(f"User {user.email} authenticated successfully")
            
            # Log user details (excluding sensitive info)
            logger.debug(f"User details - ID: {user.id}, Email: {user.email}, Tenant ID: {user.tenant_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error for email {user_login_dto.email}", exc_info=True)
            return None

class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, tenant_repository: TenantRepository):
        self.user_repository = user_repository
        self.tenant_repository = tenant_repository

    async def execute(self, user_create_dto: UserCreateDTO) -> UserDTO:
        logger.info(f"Starting registration for user: {user_create_dto.email}")
        
        try:
            # Check if user with this email already exists
            logger.info(f"Checking if email {user_create_dto.email} is already registered")
            existing_user = await self.user_repository.get_by_email(user_create_dto.email)
            if existing_user:
                error_msg = f"A user with email {user_create_dto.email} already exists"
                logger.warning(error_msg)
                raise ValueError(error_msg)

            # Check if username is taken
            logger.info(f"Checking if username {user_create_dto.username} is available")
            existing_username = await self.user_repository.get_by_username(user_create_dto.username)
            if existing_username:
                error_msg = f"Username {user_create_dto.username} is already taken"
                logger.warning(error_msg)
                raise ValueError(error_msg)

            # Check if tenant exists, if not create it
            logger.info(f"Checking for existing tenant with domain: {user_create_dto.tenant_domain}")
            tenant = await self.tenant_repository.get_by_domain(user_create_dto.tenant_domain)
            
            if not tenant:
                logger.info(f"Creating new tenant: {user_create_dto.tenant_name} ({user_create_dto.tenant_domain})")
                tenant = Tenant(
                    name=user_create_dto.tenant_name,
                    domain=user_create_dto.tenant_domain
                )
                await self.tenant_repository.add(tenant)
                role = 'admin'
                logger.info(f"Created new tenant with ID: {tenant.id}")
            else:
                role = 'user'
                logger.info(f"Using existing tenant ID: {tenant.id}")

            # Create the new user
            logger.info("Hashing password...")
            hashed_password = PasswordService.get_password_hash(user_create_dto.password)
            
            logger.info("Creating user object...")
            new_user = User(
                tenant_id=tenant.id,
                username=user_create_dto.username,
                email=user_create_dto.email,
                hashed_password=hashed_password,
                role=role
            )
            
            logger.info("Saving user to database...")
            await self.user_repository.add(new_user)
            
            logger.info(f"User {new_user.email} registered successfully with ID: {new_user.id}")
            
            # Convert to DTO for response
            user_dto = UserDTO.model_validate(new_user)
            return user_dto
            
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}", exc_info=True)
            raise
