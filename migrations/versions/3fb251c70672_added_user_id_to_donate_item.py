"""Added user_id to donate_item

Revision ID: 3fb251c70672
Revises: 54709f73890f
Create Date: 2025-01-22 02:53:10.922032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fb251c70672'
down_revision = '54709f73890f'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('donate_item')
    # Create the donate_item table with all required fields
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
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop the donate_item table if needed
    op.drop_table('donate_item')