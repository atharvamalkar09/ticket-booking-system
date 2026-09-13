# alembic/versions/e29ef4c6d54b_add_role_column_to_users.py
"""add role column to users

Revision ID: e29ef4c6d54b
Revises: a254c9c7154e
Create Date: 2026-08-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e29ef4c6d54b'
down_revision: Union[str, None] = 'a254c9c7154e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the PostgreSQL Enum type
userrole_enum = postgresql.ENUM('ADMIN', 'USER', name='userrole')


def upgrade() -> None:
    # 1. Create the PostgreSQL ENUM type explicitly
    userrole_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add the role column to users with server_default
    op.add_column(
        'users', 
        sa.Column(
            'role', 
            sa.Enum('ADMIN', 'USER', name='userrole'), 
            nullable=False, 
            server_default='USER'
        )
    )


def downgrade() -> None:
    # 1. Drop the role column
    op.drop_column('users', 'role')

    # 2. Drop the ENUM type
    userrole_enum.drop(op.get_bind(), checkfirst=True)