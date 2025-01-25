"""drop and recreate VolunteerEvents and UserVolunteer

Revision ID: 920bbd86bfb1
Revises: 204fe906457d
Create Date: 2025-01-25 23:59:09.791662

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '920bbd86bfb1'
down_revision = '204fe906457d'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the UserVolunteer table
    op.drop_table('user_volunteer')

    # Drop the VolunteerEvent table
    op.drop_table('volunteer_event')
    # Create VolunteerEvent table
    op.create_table(
        'volunteer_event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('image_file', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create UserVolunteer table
    op.create_table(
        'user_volunteer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('sign_up_date', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('attended', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['volunteer_event.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop the UserVolunteer table
    op.drop_table('user_volunteer')

    # Drop the VolunteerEvent table
    op.drop_table('volunteer_event')