"""create_news_table

Revision ID: abce5b0de640
Revises: 
Create Date: 2026-05-31 21:36:06.125215

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = 'abce5b0de640'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('news',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=1024), nullable=False),
    sa.Column('source_url', sa.String(length=2048), nullable=False),
    sa.Column('source_domain', sa.String(length=255), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('announcement', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('source_url')
    )
    op.create_index('ix_news_published_at', 'news', ['published_at'], unique=False)
    op.create_index('ix_news_source_domain', 'news', ['source_domain'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_news_source_domain', table_name='news')
    op.drop_index('ix_news_published_at', table_name='news')
    op.drop_table('news')
