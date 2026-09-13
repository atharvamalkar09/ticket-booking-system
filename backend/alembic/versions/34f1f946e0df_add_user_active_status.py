"""add user active status

Revision ID: 34f1f946e0df
Revises: fa63a1823abe
Create Date: 2026-09-02 17:07:06.577580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34f1f946e0df'
down_revision: Union[str, Sequence[str], None] = 'fa63a1823abe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true')
        )
    )


def downgrade() -> None:
    op.drop_column('users', 'is_active')
