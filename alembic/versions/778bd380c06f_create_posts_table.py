"""create posts table

Revision ID: 778bd380c06f
Revises: 
Create Date: 2022-01-01 15:40:42.215447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '778bd380c06f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
    sa.Column('title', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_table('posts')
