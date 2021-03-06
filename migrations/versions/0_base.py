"""base

Revision ID: 0
Revises: 
Create Date: 2019-01-08 23:32:36.076134

"""
import geoalchemy2
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.get_bind().execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.create_table(
        'gis_polygon',
        sa.Column('_created', sa.DateTime(), nullable=False),
        sa.Column('_edited', sa.DateTime(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.VARCHAR(), nullable=True),
        sa.Column('props', sa.JSON(), nullable=True),
        sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.get_bind().execute('DROP EXTENSION postgis CASCADE')
    op.drop_table('gis_polygon')
    # ### end Alembic commands ###
