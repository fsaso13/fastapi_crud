"""Add content column to posts table

Revision ID: d50e311be966
Revises: 7c846c582e89
Create Date: 2024-05-19 19:07:21.235926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd50e311be966'
down_revision: Union[str, None] = '7c846c582e89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
