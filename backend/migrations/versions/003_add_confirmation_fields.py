"""add confirmation fields to participants

Revision ID: 003_add_confirmation_fields
Revises: 002_add_participant_fields
Create Date: 2026-03-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_confirmation_fields'
down_revision = '002_add_participant_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('participants', sa.Column('is_confirmed', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('participants', sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('participants', sa.Column('confirmation_token', sa.String(length=255), nullable=True))
    op.create_unique_constraint('uq_participants_confirmation_token', 'participants', ['confirmation_token'])
    op.add_column('participants', sa.Column('last_email_sent_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('participants', sa.Column('reminder_count', sa.Integer(), nullable=False, server_default="0"))


def downgrade():
    op.drop_column('participants', 'reminder_count')
    op.drop_column('participants', 'last_email_sent_at')
    op.drop_constraint('uq_participants_confirmation_token', 'participants', type_='unique')
    op.drop_column('participants', 'confirmation_token')
    op.drop_column('participants', 'confirmed_at')
    op.drop_column('participants', 'is_confirmed')
