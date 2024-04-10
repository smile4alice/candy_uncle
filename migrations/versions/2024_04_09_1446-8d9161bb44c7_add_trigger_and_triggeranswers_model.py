"""add trigger and triggeranswers model

Revision ID: 8d9161bb44c7
Revises: 0aa71f68df59
Create Date: 2024-04-09 14:46:22.056317

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8d9161bb44c7"
down_revision: Union[str, None] = "0aa71f68df59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "triggers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "match_type", sa.Enum("text", "regex", name="matchtypeenum"), nullable=False
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("trigger", sa.String(length=4096), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "trigger_answer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "media_type",
            sa.Enum(
                "TEXT",
                "PHOTO",
                "STICKER",
                "VIDEO",
                "VOICE",
                "AUDIO",
                name="mediatypeenum",
            ),
            nullable=False,
        ),
        sa.Column("answer", sa.String(length=4096), nullable=False),
        sa.Column("trigger_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["trigger_id"],
            ["triggers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.alter_column(
        "base_commands",
        "name",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "base_commands",
        "name",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
    )
    op.drop_table("trigger_answer")
    op.drop_table("triggers")
    # ### end Alembic commands ###
