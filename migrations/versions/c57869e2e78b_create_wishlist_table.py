"""create wishlist table

Revision ID: c57869e2e78b
Revises: 2be0158f74b3
Create Date: 2025-02-13 23:17:01.950922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c57869e2e78b'
down_revision = '2be0158f74b3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'wishlist',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', sa.Integer, sa.ForeignKey('volunteer_event.id'), nullable=False)
    )

def downgrade():
    op.drop_table('wishlist')