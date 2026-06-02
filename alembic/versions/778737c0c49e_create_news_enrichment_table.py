"""create_news_enrichment_table

Revision ID: 778737c0c49e
Revises: abce5b0de640
Create Date: 2026-06-01 18:50:42.488140

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "778737c0c49e"
down_revision: Union[str, Sequence[str], None] = "abce5b0de640"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "news_enrichment",
        sa.Column("news_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("enriched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("parser_used", sa.String(length=128), nullable=True),
        sa.Column("full_text", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=512), nullable=True),
        sa.Column("main_image_url", sa.String(length=2048), nullable=True),
        sa.Column("images", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "categories", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("views_count", sa.Integer(), nullable=True),
        sa.Column("comments_count", sa.Integer(), nullable=True),
        sa.Column(
            "article_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["news_id"], ["news.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("news_id"),
        sa.UniqueConstraint("news_id", name="uq_enrichment_news_id"),
    )
    op.create_index(
        "ix_enrichment_status", "news_enrichment", ["status"], unique=False
    )
    op.create_index(
        "ix_enrichment_search_vector",
        "news_enrichment",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_enrichment_search_vector",
        table_name="news_enrichment",
        postgresql_using="gin",
    )
    op.drop_index("ix_enrichment_status", table_name="news_enrichment")
    op.drop_table("news_enrichment")
