"""remove deprecated user fields

Revision ID: 5ed672b345f6
Revises: 2cf9d85789df
Create Date: 2024-02-19 18:00:41.703207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ed672b345f6'
down_revision: Union[str, None] = '2cf9d85789df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'longest_streak')
    op.drop_column('user', 'looses')
    op.drop_column('user', 'skip_count')
    op.drop_column('user', 'last_game_at')
    op.drop_column('user', 'wins')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('wins', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('last_game_at', sa.DATE(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('skip_count', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('looses', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('longest_streak', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
