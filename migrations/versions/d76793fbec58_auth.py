"""create_auth_tables

Revision ID: 4a75f0d93503
Revises: 
Create Date: 2025-05-01 18:34:29.891542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'd76793fbec58_auth'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('blacklisted_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_blacklisted_tokens_id'), 'blacklisted_tokens', ['id'], unique=False)

    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('user_type', sa.Enum('CUSTOMER', 'FREELANCER', name='usertype'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_blacklisted_tokens_id'), table_name='blacklisted_tokens')
    op.drop_table('blacklisted_tokens')