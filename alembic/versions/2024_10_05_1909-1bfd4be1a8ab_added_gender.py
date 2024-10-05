"""added gender

Revision ID: 1bfd4be1a8ab
Revises: 5db00320dfe4
Create Date: 2024-10-05 19:09:11.078001+03:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1bfd4be1a8ab'
down_revision: Union[str, None] = '5db00320dfe4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adding stuff."""
    op.add_column(
        'users',
        sa.Column('gender', sa.Boolean, nullable=True),
    )


def downgrade() -> None:
    """Removing stuff."""
    op.drop_column('users', 'gender')
