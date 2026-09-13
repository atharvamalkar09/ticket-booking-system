"""add payment failed booking status

Revision ID: 8186fb84ee90
Revises: ca01b88e3b27
Create Date: 2026-09-08 10:58:02.703513

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8186fb84ee90'
down_revision: Union[str, Sequence[str], None] = 'ca01b88e3b27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE booking_status_enum ADD VALUE IF NOT EXISTS 'PAYMENT_FAILED'"
    )


def downgrade() -> None:
    pass