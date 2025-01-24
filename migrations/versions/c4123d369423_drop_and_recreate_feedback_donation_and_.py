"""drop and recreate Feedback, Donation and Organization tables

Revision ID: c4123d369423
Revises: c57bb2655981
Create Date: 2025-01-24 10:37:23.116162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4123d369423'
down_revision = 'c57bb2655981'
branch_labels = None
depends_on = None


def upgrade():
    # Drop tables if they exist
    op.drop_table('feedback')
    op.drop_table('donations')
    op.drop_table('organization')

    # Recreate the tables
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('issue', sa.Integer(), nullable=False),
        sa.Column('feedback_date', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'donations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('organization', sa.String(length=100), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'organization',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop tables in the downgrade migration
    op.drop_table('feedback')
    op.drop_table('donations')
    op.drop_table('organization')