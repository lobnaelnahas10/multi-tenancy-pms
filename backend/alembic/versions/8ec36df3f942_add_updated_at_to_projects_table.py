"""Add updated_at to projects table

Revision ID: 8ec36df3f942
Revises: 316598a009fb
Create Date: 2025-08-19 14:19:25.736098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ec36df3f942'
down_revision: Union[str, Sequence[str], None] = '316598a009fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    # Set initial value for existing records
    op.execute("UPDATE projects SET updated_at = created_at")
    # Make the column NOT NULL after setting values
    op.alter_column('projects', 'updated_at', nullable=False, server_default=sa.text('now()'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'updated_at')
