"""empty message

Revision ID: 046cef97ce6e
Revises: d5c41039e31a
Create Date: 2016-06-02 13:39:24.953545

"""

# revision identifiers, used by Alembic.
revision = '046cef97ce6e'
down_revision = 'd5c41039e31a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('agency', 'tag',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=30),
               existing_nullable=True)
    op.alter_column('route', 'tag',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=30),
               existing_nullable=True)
    op.alter_column('stop', 'tag',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=30),
               existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('stop', 'tag',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    op.alter_column('route', 'tag',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    op.alter_column('agency', 'tag',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    ### end Alembic commands ###
