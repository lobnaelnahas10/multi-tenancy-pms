"""Add updated_at column to projects table

Revision ID: 6c2e018e0433
Revises: 8ec36df3f942
Create Date: 2025-08-19 14:31:15.630209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c2e018e0433'
down_revision: Union[str, Sequence[str], None] = '8ec36df3f942'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'updated_at')
