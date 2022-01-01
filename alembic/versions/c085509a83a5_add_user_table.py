"""add user table

Revision ID: c085509a83a5
Revises: babeca0a8d8b
Create Date: 2022-01-01 15:55:17.542481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c085509a83a5'
down_revision = 'babeca0a8d8b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('email', sa.String(), nullable=False),
                sa.Column('password', sa.String(), nullable=False),
                sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                        server_default=sa.text('now()'), nullable=False),
                sa.PrimaryKeyConstraint('id'),
                sa.UniqueConstraint('email')
                )
    pass


def downgrade():
    op.drop_table('users')
    pass
