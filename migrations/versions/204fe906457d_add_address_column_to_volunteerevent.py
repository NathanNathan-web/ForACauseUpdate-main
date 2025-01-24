"""Add address column to VolunteerEvent

Revision ID: 204fe906457d
Revises: 8b022ce64347
Create Date: 2025-01-24 20:52:20.742592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '204fe906457d'
down_revision = '8b022ce64347'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing VolunteerEvent table
    op.drop_table('volunteer_event')

    # Recreate the VolunteerEvent table with correct columns
    op.create_table(
        'volunteer_event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=True),  # New column for address
        sa.Column('image_file', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop the newly created VolunteerEvent table
    op.drop_table('volunteer_event')

    # Recreate the VolunteerEvent table without the address column
    op.create_table(
        'volunteer_event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('image_file', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )