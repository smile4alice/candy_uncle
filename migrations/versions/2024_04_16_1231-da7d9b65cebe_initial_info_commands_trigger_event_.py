"""initial info_commands, trigger_event, trigger tables

Revision ID: da7d9b65cebe
Revises:
Create Date: 2024-04-16 12:31:39.828555

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "da7d9b65cebe"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "info_commands",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("info", sa.String(length=4096), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "trigger_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "match_type",
            sa.Enum("text", "regex", name="matchmodeenum"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("event", sa.String(length=4096), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "triggers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "media_type",
            sa.Enum(
                "TEXT",
                "PHOTO",
                "ANIMATION",
                "STICKER",
                "VIDEO",
                "VOICE",
                "AUDIO",
                name="mediatypeenum",
            ),
            nullable=False,
        ),
        sa.Column("media", sa.String(length=4096), nullable=False),
        sa.Column("trigger_event_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["trigger_event_id"],
            ["trigger_events.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("triggers")
    op.drop_table("trigger_events")
    op.drop_table("info_commands")
    # ### end Alembic commands ###
