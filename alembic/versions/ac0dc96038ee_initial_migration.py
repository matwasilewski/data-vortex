"""Initial migration

Revision ID: ac0dc96038ee
Revises: 
Create Date: 2024-05-04 16:49:12.002156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac0dc96038ee'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rental_listings',
    sa.Column('property_id', sa.String(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('price_amount', sa.Float(), nullable=True),
    sa.Column('price_per', sa.String(), nullable=True),
    sa.Column('price_currency', sa.String(), nullable=True),
    sa.Column('added_date', sa.Date(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('postcode', sa.String(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('property_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rental_listings')
    # ### end Alembic commands ###
