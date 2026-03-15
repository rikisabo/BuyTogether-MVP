"""add participant address and contact fields

Revision ID: 002_add_participant_fields
Revises: 001_initial_schema
Create Date: 2026-03-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_participant_fields'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('participants', sa.Column('city', sa.String(length=255), nullable=True))
    op.add_column('participants', sa.Column('street', sa.String(length=255), nullable=True))
    op.add_column('participants', sa.Column('house_number', sa.String(length=50), nullable=True))
    op.add_column('participants', sa.Column('apartment', sa.String(length=50), nullable=True))
    op.add_column('participants', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('participants', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('participants', 'notes')
    op.drop_column('participants', 'phone')
    op.drop_column('participants', 'apartment')
    op.drop_column('participants', 'house_number')
    op.drop_column('participants', 'street')
    op.drop_column('participants', 'city')
