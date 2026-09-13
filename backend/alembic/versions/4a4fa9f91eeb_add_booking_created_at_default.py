"""add booking created_at default

Revision ID: 4a4fa9f91eeb
Revises: 8186fb84ee90
Create Date: 2026-09-08 17:41:45.854098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a4fa9f91eeb'
down_revision: Union[str, Sequence[str], None] = '8186fb84ee90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
