"""merge heads

Revision ID: 316598a009fb
Revises: 1a2b3c4d5e6f, babf3a77b074
Create Date: 2025-08-19 14:18:59.077348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '316598a009fb'
down_revision: Union[str, Sequence[str], None] = ('1a2b3c4d5e6f', 'babf3a77b074')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
