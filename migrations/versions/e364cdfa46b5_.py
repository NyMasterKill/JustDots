"""empty message

Revision ID: e364cdfa46b5
Revises: d1e4920698f8, f75b31c21ddc
Create Date: 2025-05-08 23:13:06.239948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e364cdfa46b5'
down_revision: Union[str, None] = '7284f8dd7908'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass