"""add title_poky_id to user

Revision ID: 289ae42742bf
Revises: dca6219d6f9f
Create Date: 2024-02-27 01:05:56.417967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '289ae42742bf'
down_revision: Union[str, None] = 'dca6219d6f9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('title_poky_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'poky_ball', ['title_poky_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'title_poky_id')
    # ### end Alembic commands ###