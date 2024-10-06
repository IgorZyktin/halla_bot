"""added preffered model

Revision ID: d792e5b0837c
Revises: 1bfd4be1a8ab
Create Date: 2024-10-06 12:43:59.659259+03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd792e5b0837c'
down_revision: Union[str, None] = '1bfd4be1a8ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adding stuff."""
    op.add_column(
        'users',
        sa.Column('model', sa.String, nullable=True),
    )


def downgrade() -> None:
    """Removing stuff."""
    op.drop_column('users', 'model')
