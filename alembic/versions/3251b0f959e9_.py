"""empty message

Revision ID: 3251b0f959e9
Revises: 1c4b1bca73bc
Create Date: 2015-05-04 10:27:52.894901

"""

# revision identifiers, used by Alembic.
revision = '3251b0f959e9'
down_revision = '1c4b1bca73bc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('yt_player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.Column('name_en', sa.String(length=30), nullable=True),
    sa.Column('position', sa.String(length=10), nullable=True),
    sa.Column('height', sa.Float(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('country', sa.String(length=30), nullable=True),
    sa.Column('country_en', sa.String(length=30), nullable=True),
    sa.Column('birthday', sa.DateTime(), nullable=True),
    sa.Column('age', sa.SmallInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player_number',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('number', sa.SmallInteger(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['yt_player.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['yt_team.id'], ),
    sa.PrimaryKeyConstraint('id', 'player_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player_number')
    op.drop_table('yt_player')
    ### end Alembic commands ###