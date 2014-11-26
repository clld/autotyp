"""fix polymorphic_type

Revision ID: 3cbd4ad7e495
Revises: 
Create Date: 2014-11-26 13:57:23.031000

"""

# revision identifiers, used by Alembic.
revision = '3cbd4ad7e495'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    update_pmtype(['language'], 'base', 'custom')


def downgrade():
    update_pmtype(['language'], 'custom', 'base')


def update_pmtype(tablenames, before, after):
    for table in tablenames:
        op.execute(sa.text('UPDATE %s SET polymorphic_type = :after '
            'WHERE polymorphic_type = :before' % table
            ).bindparams(before=before, after=after))
