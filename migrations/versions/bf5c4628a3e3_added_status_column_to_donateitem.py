"""Added status column to DonateItem

Revision ID: bf5c4628a3e3
Revises: 3fb251c70672
Create Date: 2025-01-22 21:04:43.701325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf5c4628a3e3'
down_revision = '3fb251c70672'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing table
    op.drop_table('donate_item')

    # Recreate the table
    op.create_table(
        'donate_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('condition', sa.String(length=10), nullable=False),
        sa.Column('image_file', sa.String(length=200), nullable=True),
        sa.Column('preferred_drop_off_method', sa.String(length=50), nullable=False),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('preferred_date', sa.Date(), nullable=True),
        sa.Column('preferred_time', sa.Time(), nullable=True),
        sa.Column('organisation', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='Pending'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop the table if we need to downgrade
    op.drop_table('donate_item')