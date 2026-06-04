"""with_change

Revision ID: b1a3513a4176
Revises: fcc3ae6b807c
Create Date: 2026-06-04 09:56:28.607456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1a3513a4176'
down_revision: Union[str, None] = 'fcc3ae6b807c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'campaign',
        'change_required',
        new_column_name='with_change',
        existing_type=sa.Boolean(),
        existing_nullable=False,
        existing_server_default=sa.sql.expression.true(),
    )


def downgrade() -> None:
    op.alter_column(
        'campaign',
        'with_change',
        new_column_name='change_required',
        existing_type=sa.Boolean(),
        existing_nullable=False,
        existing_server_default=sa.sql.expression.true(),
    )
