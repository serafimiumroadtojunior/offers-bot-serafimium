"""Table for tracking recent users

Revision ID: 0373590c431a
Revises: 18a9d240e228
Create Date: 2025-05-25 17:58:51.214815

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0373590c431a'
down_revision: Union[str, None] = '18a9d240e228'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'late_users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('full_name', sa.String(100)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

    sa.UniqueConstraint('user_id', name='uq_user_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('late_users')