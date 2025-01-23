"""Recreate donate_item table with user_id

Revision ID: 54709f73890f
Revises: 
Create Date: 2025-01-22 02:48:35.407311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54709f73890f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old donate_item table if it exists
    op.drop_table('donate_item')
    
    # Recreate the donate_item table with the user_id column
    op.create_table(
        'donate_item',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        # Add any other columns here as needed
    )

def downgrade():
    # Drop the newly created donate_item table if we need to rollback
    op.drop_table('donate_item')
    
    # Optionally, you could recreate the old table here if needed
    op.create_table(
        'donate_item',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        # Old table columns without user_id
    )
