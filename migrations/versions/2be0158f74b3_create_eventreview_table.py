"""create eventreview table

Revision ID: 2be0158f74b3
Revises: d9e7e818bfee
Create Date: 2025-02-13 22:52:13.335346

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '2be0158f74b3'
down_revision = 'd9e7e818bfee'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_review',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_id', sa.Integer, sa.ForeignKey('volunteer_event.id'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('likes', sa.Integer, default=0),
        sa.Column('dislikes', sa.Integer, default=0)
    )


def downgrade():
    op.drop_table('event_review')