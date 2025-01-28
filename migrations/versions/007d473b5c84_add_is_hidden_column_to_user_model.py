"""Add is_hidden column to User model and fix wishlist foreign key constraint

Revision ID: 007d473b5c84
Revises: 55abdd46825f
Create Date: 2025-01-28 14:14:57.855857
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007d473b5c84'
down_revision = '55abdd46825f'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('event_review') as batch_op:
        batch_op.add_column(sa.Column('likes', sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column('dislikes', sa.Integer(), nullable=False, server_default="0"))

def downgrade():
    with op.batch_alter_table('event_review') as batch_op:
        batch_op.drop_column('likes')
        batch_op.drop_column('dislikes')
