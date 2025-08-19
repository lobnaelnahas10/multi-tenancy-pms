from typing import List, Optional
import uuid
from domain.entities import User
from domain.repositories import ProjectUserRepository

class GetProjectUsersUseCase:
    def __init__(self, project_user_repository: ProjectUserRepository):
        self.project_user_repository = project_user_repository

    async def execute(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> List[User]:
        """
        Get all users associated with a project
        
        Args:
            project_id: The ID of the project
            tenant_id: The ID of the tenant (for authorization)
            
        Returns:
            List of User objects
        """
        try:
            users = await self.project_user_repository.get_users_by_project(project_id, tenant_id)
            return users
        except Exception as e:
            # Log the error and re-raise with a more specific message
            raise Exception(f"Failed to fetch users for project {project_id}: {str(e)}")
