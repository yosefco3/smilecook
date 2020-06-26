"""empty message

Revision ID: 159051552c77
Revises: e29b6aedd609
Create Date: 2020-06-24 21:34:03.986189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '159051552c77'
down_revision = 'e29b6aedd609'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('cover_image', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe', 'cover_image')
    # ### end Alembic commands ###