"""Add paper metadata fields

Revision ID: 1a6805a5758a
Revises:
Create Date: 2026-09-19 05:47:28.890124
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1a6805a5758a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add timestamp columns as nullable first.
    # This is required because the papers table already contains data.
    op.add_column(
        "papers",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "papers",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # Populate timestamps for existing records.
    op.execute(
        sa.text(
            """
            UPDATE papers
            SET created_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
               OR updated_at IS NULL
            """
        )
    )

    # Now that all existing records have values, enforce NOT NULL.
    with op.batch_alter_table("papers", recreate="always") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
        )

        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table("papers", recreate="always") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("keywords")
        batch_op.drop_column("journal")
        batch_op.drop_column("doi")
        batch_op.drop_column("publication_year")
        batch_op.drop_column("abstract")