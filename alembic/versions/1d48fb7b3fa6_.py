"""empty message

Revision ID: 1d48fb7b3fa6
Revises: 4de72dd4dad9
Create Date: 2015-05-04 11:20:08.173639

"""

# revision identifiers, used by Alembic.
revision = '1d48fb7b3fa6'
down_revision = '4de72dd4dad9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('league_team',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('league_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['league_id'], ['yt_league.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['yt_team.id'], ),
    sa.PrimaryKeyConstraint('team_id', 'league_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('league_team')
    ### end Alembic commands ###
