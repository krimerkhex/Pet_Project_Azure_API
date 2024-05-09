"""Create tables for users, tasks and achievements

Revision ID: 509f7a41ec5b
Revises: 
Create Date: 2024-05-09 21:07:20.222560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '509f7a41ec5b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'Users',
        sa.Column('ID', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('Name', sa.String(length=255), nullable=False),
    )

    op.create_table(
        'Tasks',
        sa.Column('ID', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('User_ID', sa.Integer, sa.ForeignKey('Users.ID')),
        sa.Column('Type', sa.String(length=255), nullable=False),
        sa.Column('Title', sa.String(length=255), nullable=False),
        sa.Column('Status', sa.String(length=255), nullable=False),
        sa.Column('Reason', sa.String(length=255), nullable=False),
    )

    op.create_table(
        'Achievement',
        sa.Column('ID', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('User_ID', sa.Integer, sa.ForeignKey('Users.ID')),
        sa.Column('Title', sa.String(length=255), nullable=False),
        sa.Column('Description', sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('Achievement')
    op.drop_table('Tasks')
    op.drop_table('Users')
