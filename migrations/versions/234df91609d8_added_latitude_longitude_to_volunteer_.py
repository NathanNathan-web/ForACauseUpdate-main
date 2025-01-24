"""Added latitude, longitude to volunteer_event table

Revision ID: 234df91609d8
Revises: c4123d369423
Create Date: 2025-01-24 20:22:15.706034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '234df91609d8'
down_revision = 'c4123d369423'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the table if it exists
    op.drop_table('volunteer_event')

    # Recreate the table with updated schema
    op.create_table(
        'volunteer_event',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('image_file', sa.String(length=100), nullable=True)
    )


def downgrade():
    # Drop the updated table
    op.drop_table('volunteer_event')

    # Recreate the original table without latitude and longitude
    op.create_table(
        'volunteer_event',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('image_file', sa.String(length=100), nullable=True)
    )