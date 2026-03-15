"""Initial migration - create deals and participants tables with enums, indexes, and constraints.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # Define enums once
    deal_status_enum = postgresql.ENUM(
        "ACTIVE", "CLOSED", "FAILED", name="dealstatus"
    )
    participant_state_enum = postgresql.ENUM(
        "JOINED", "INVITED_TO_PAY", "PAID", "CANCELLED", name="participantstate"
    )

    # Create enums safely (won't error if already exists)
    deal_status_enum.create(bind, checkfirst=True)
    participant_state_enum.create(bind, checkfirst=True)

    # IMPORTANT: use create_type=False in columns so table creation won't try to create enum again
    deal_status_col_enum = postgresql.ENUM(
        "ACTIVE", "CLOSED", "FAILED", name="dealstatus", create_type=False
    )
    participant_state_col_enum = postgresql.ENUM(
        "JOINED", "INVITED_TO_PAY", "PAID", "CANCELLED", name="participantstate", create_type=False
    )

    # Create deals table
    op.create_table(
        "deals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("min_qty_to_close", sa.Integer(), nullable=False),
        sa.Column("current_qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            deal_status_col_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Index on deals.status
    op.create_index("ix_deals_status", "deals", ["status"])

    # Create participants table
    op.create_table(
        "participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "state",
            participant_state_col_enum,
            nullable=False,
            server_default="JOINED",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("deal_id", "email", name="uq_participants_deal_email"),
    )

    # Indexes on participants
    op.create_index("ix_participants_deal_id", "participants", ["deal_id"])
    op.create_index("ix_participants_email", "participants", ["email"])


def downgrade() -> None:
    bind = op.get_bind()

    # Drop indexes
    op.drop_index("ix_participants_email", table_name="participants")
    op.drop_index("ix_participants_deal_id", table_name="participants")
    op.drop_index("ix_deals_status", table_name="deals")

    # Drop tables
    op.drop_table("participants")
    op.drop_table("deals")

    # Drop enums safely
    deal_status_enum = postgresql.ENUM(
        "ACTIVE", "CLOSED", "FAILED", name="dealstatus"
    )
    participant_state_enum = postgresql.ENUM(
        "JOINED", "INVITED_TO_PAY", "PAID", "CANCELLED", name="participantstate"
    )

    participant_state_enum.drop(bind, checkfirst=True)
    deal_status_enum.drop(bind, checkfirst=True)