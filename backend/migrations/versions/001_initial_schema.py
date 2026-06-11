"""Initial schema — accounts, usage, quota, alerts, gemini config.

Revision ID: 001_initial
Revises:
Create Date: 2026-06-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("gmail_slot", sa.String(length=16), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "gemini_quota_config",
        sa.Column("model_id", sa.String(length=128), nullable=False),
        sa.Column("model_label", sa.String(length=128), nullable=False),
        sa.Column("rpm", sa.Integer(), nullable=False),
        sa.Column("tpm", sa.Integer(), nullable=False),
        sa.Column("rpd", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("model_id"),
    )

    op.create_table(
        "usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("model_id", sa.String(length=128), nullable=False),
        sa.Column("model_label", sa.String(length=128), nullable=False),
        sa.Column("input_tokens", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("output_tokens", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("cache_tokens", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("cost_usd", sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column("request_type", sa.String(length=32), nullable=True),
        sa.Column("external_id", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usage_records_account_id", "usage_records", ["account_id"])
    op.create_index("ix_usage_records_source", "usage_records", ["source"])
    op.create_index("ix_usage_records_timestamp", "usage_records", ["timestamp"])
    op.create_index("ix_usage_records_model_id", "usage_records", ["model_id"])

    op.create_table(
        "quota_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("model_id", sa.String(length=128), nullable=False),
        sa.Column("model_label", sa.String(length=128), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(), nullable=False),
        sa.Column("quota_remaining_pct", sa.Float(), nullable=True),
        sa.Column("is_exhausted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("requests_used", sa.Integer(), nullable=True),
        sa.Column("requests_total", sa.Integer(), nullable=True),
        sa.Column("credits_used", sa.Numeric(precision=14, scale=6), nullable=True),
        sa.Column("credits_total", sa.Numeric(precision=14, scale=6), nullable=True),
        sa.Column("reset_at", sa.DateTime(), nullable=True),
        sa.Column("reset_cadence", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quota_snapshots_account_id", "quota_snapshots", ["account_id"])
    op.create_index("ix_quota_snapshots_source", "quota_snapshots", ["source"])
    op.create_index("ix_quota_snapshots_model_id", "quota_snapshots", ["model_id"])
    op.create_index("ix_quota_snapshots_snapshot_at", "quota_snapshots", ["snapshot_at"])

    op.create_table(
        "alert_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=True),
        sa.Column("model_id", sa.String(length=128), nullable=True),
        sa.Column("threshold_pct", sa.Float(), nullable=False),
        sa.Column("channel", sa.String(length=16), nullable=False),
        sa.Column("webhook_url", sa.String(length=512), nullable=True),
        sa.Column("cooldown_minutes", sa.Integer(), nullable=False, server_default=sa.text("60")),
        sa.Column("last_fired_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("alert_rules")
    op.drop_index("ix_quota_snapshots_snapshot_at", table_name="quota_snapshots")
    op.drop_index("ix_quota_snapshots_model_id", table_name="quota_snapshots")
    op.drop_index("ix_quota_snapshots_source", table_name="quota_snapshots")
    op.drop_index("ix_quota_snapshots_account_id", table_name="quota_snapshots")
    op.drop_table("quota_snapshots")
    op.drop_index("ix_usage_records_model_id", table_name="usage_records")
    op.drop_index("ix_usage_records_timestamp", table_name="usage_records")
    op.drop_index("ix_usage_records_source", table_name="usage_records")
    op.drop_index("ix_usage_records_account_id", table_name="usage_records")
    op.drop_table("usage_records")
    op.drop_table("gemini_quota_config")
    op.drop_table("accounts")
