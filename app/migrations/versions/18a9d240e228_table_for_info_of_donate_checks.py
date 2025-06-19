"""Table for info of donate checks

Revision ID: 18a9d240e228
Revises: 
Create Date: 2025-05-25 17:21:48.870375

"""
from typing import Sequence, Union
from datetime import timedelta

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18a9d240e228'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'donate_checks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('charge_id', sa.String(100)),
        sa.Column('check_id', sa.String(100)),
        sa.Column('stars_amount', sa.Integer),
        sa.Column('deleted_at', sa.DateTime, default=timedelta(days=7))
    )

    op.create_index('uq_user_id', 'donate_checks', ['user_id'])
    op.create_unique_constraint('uq_check_id', 'donate_checks', ['check_id'])
    op.create_unique_constraint('uq_charge_id', 'donate_checks', ['charge_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('donate_checks')