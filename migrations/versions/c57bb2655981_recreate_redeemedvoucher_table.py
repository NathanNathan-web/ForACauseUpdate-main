"""recreate RedeemedVoucher table

Revision ID: c57bb2655981
Revises: bf5c4628a3e3
Create Date: 2025-01-24 10:07:49.676192

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c57bb2655981'
down_revision = 'bf5c4628a3e3'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing RedeemedVouchers table if it exists
    op.drop_table('redeemed_vouchers', if_exists=True)

    # Create the RedeemedVouchers table
    op.create_table(
        'redeemed_vouchers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('status', sa.Integer, nullable=False, default=1),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('voucher_id', sa.Integer, sa.ForeignKey('voucher.id'), nullable=True),
    )


def downgrade():
    # Revert the migration by dropping the RedeemedVouchers table
    op.drop_table('redeemed_vouchers')