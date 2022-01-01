"""add content to posts table

Revision ID: babeca0a8d8b
Revises: 778bd380c06f
Create Date: 2022-01-01 15:50:47.366077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'babeca0a8d8b'
down_revision = '778bd380c06f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
