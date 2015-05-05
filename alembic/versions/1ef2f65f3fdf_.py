"""empty message

Revision ID: 1ef2f65f3fdf
Revises: 20bd1f97446f
Create Date: 2015-05-05 17:48:30.322935

"""

# revision identifiers, used by Alembic.
revision = '1ef2f65f3fdf'
down_revision = '20bd1f97446f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('league_team', 'league_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True,
               existing_server_default=sa.text(u"'0'"))
    op.alter_column('league_team', 'team_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True,
               existing_server_default=sa.text(u"'0'"))
    op.add_column('yt_match', sa.Column('time', sa.Time(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('yt_match', 'time')
    op.alter_column('league_team', 'team_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False,
               existing_server_default=sa.text(u"'0'"))
    op.alter_column('league_team', 'league_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False,
               existing_server_default=sa.text(u"'0'"))
    ### end Alembic commands ###
