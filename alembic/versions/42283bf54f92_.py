"""empty message

Revision ID: 42283bf54f92
Revises: 39cef477fe93
Create Date: 2015-06-11 17:18:14.417441

"""

# revision identifiers, used by Alembic.
revision = '42283bf54f92'
down_revision = '39cef477fe93'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player_match', sa.Column('appear', sa.SmallInteger(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player_match', 'appear')
    ### end Alembic commands ###
