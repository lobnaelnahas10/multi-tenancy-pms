"""Add project_users table

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2025-08-19 13:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create project_users table
    op.create_table(
        'project_users',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='member'),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'user_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_project_users_project_id'), 'project_users', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_users_user_id'), 'project_users', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_project_users_user_id'), table_name='project_users')
    op.drop_index(op.f('ix_project_users_project_id'), table_name='project_users')
    op.drop_table('project_users')
