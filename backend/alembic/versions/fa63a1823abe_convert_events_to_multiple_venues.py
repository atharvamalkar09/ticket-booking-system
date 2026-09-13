"""convert events to multiple venues

Revision ID: fa63a1823abe
Revises: 2bcc246cc38a
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fa63a1823abe"
down_revision: Union[str, Sequence[str], None] = "2bcc246cc38a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Create event_venues association table
    op.create_table(
        "event_venues",

        sa.Column(
            "event_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "venue_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["venue_id"],
            ["venues.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "event_id",
            "venue_id",
        ),
    )

    # 2. Preserve existing event -> venue relationships
    op.execute(
        """
        INSERT INTO event_venues (event_id, venue_id)
        SELECT id, venue_id
        FROM events
        WHERE venue_id IS NOT NULL
        """
    )

    # 3. Remove old foreign key
    op.drop_constraint(
        "events_venue_id_fkey",
        "events",
        type_="foreignkey",
    )

    # 4. Remove old venue_id column
    op.drop_column(
        "events",
        "venue_id",
    )


def downgrade() -> None:

    # 1. Recreate venue_id column
    op.add_column(
        "events",
        sa.Column(
            "venue_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # 2. Restore one venue per event
    #
    # If an event had multiple venues,
    # downgrade keeps the lowest venue_id.
    op.execute(
        """
        UPDATE events e
        SET venue_id = ev.venue_id
        FROM (
            SELECT DISTINCT ON (event_id)
                event_id,
                venue_id
            FROM event_venues
            ORDER BY event_id, venue_id
        ) ev
        WHERE e.id = ev.event_id
        """
    )

    # 3. Restore NOT NULL constraint
    op.alter_column(
        "events",
        "venue_id",
        nullable=False,
    )

    # 4. Restore foreign key
    op.create_foreign_key(
        "events_venue_id_fkey",
        "events",
        "venues",
        ["venue_id"],
        ["id"],
    )

    # 5. Remove association table
    op.drop_table(
        "event_venues",
    )