"""recreate uservolunteer table

Revision ID: 8b022ce64347
Revises: 234df91609d8
Create Date: 2025-01-24 20:35:42.604813

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '8b022ce64347'
down_revision = '234df91609d8'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing table if it exists
    op.drop_table('user_volunteer')

    # Create the table with the new model
    op.create_table(
        'user_volunteer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('sign_up_date', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('attended', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['user.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['event_id'], ['volunteer_event.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop the newly created table in case of rollback
    op.drop_table('user_volunteer')