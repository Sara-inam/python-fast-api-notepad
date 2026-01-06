"""Add summary column and note_category table

Revision ID: 807428f0dacd
Revises: e1f62da85c2f
Create Date: 2026-01-01 16:57:24.632701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '807428f0dacd'
down_revision: Union[str, Sequence[str], None] = 'e1f62da85c2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add summary column to notes table
    op.add_column('notes', sa.Column('summary', sa.Text(), nullable=True))

    # Create categories table if it doesn't exist
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )

    # Create note_category many-to-many table
    op.create_table(
        'note_category',
        sa.Column('note_id', sa.Integer, sa.ForeignKey('notes.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('note_category')
    op.drop_table('categories')
    op.drop_column('notes', 'summary')
