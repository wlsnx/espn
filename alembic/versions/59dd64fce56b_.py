"""empty message

Revision ID: 59dd64fce56b
Revises: 21c475a3fecc
Create Date: 2015-05-07 15:56:49.950673

"""

# revision identifiers, used by Alembic.
revision = '59dd64fce56b'
down_revision = '21c475a3fecc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player_match', sa.Column('saving', sa.SmallInteger(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player_match', 'saving')
    ### end Alembic commands ###
