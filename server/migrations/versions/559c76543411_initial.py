"""initial

Revision ID: 559c76543411
Revises: 
Create Date: 2024-05-13 04:59:51.973720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '559c76543411'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('img', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('_password_hash', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('img', sa.String(), nullable=True),
    sa.Column('contacts', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_users_category_id_categories')),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('donationrequest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ngo_id', sa.Integer(), nullable=True),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('donor_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('amount_requested', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['users.id'], name=op.f('fk_donationrequest_admin_id_users')),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_donationrequest_category_id_categories')),
    sa.ForeignKeyConstraint(['donor_id'], ['users.id'], name=op.f('fk_donationrequest_donor_id_users')),
    sa.ForeignKeyConstraint(['ngo_id'], ['users.id'], name=op.f('fk_donationrequest_ngo_id_users')),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('donations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('donor_id', sa.Integer(), nullable=True),
    sa.Column('donation_request_id', sa.Integer(), nullable=True),
    sa.Column('ngo_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('date_donated', sa.DateTime(), nullable=True),
    sa.Column('pay_method', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_donations_category_id_categories')),
    sa.ForeignKeyConstraint(['donation_request_id'], ['donationrequest.id'], name=op.f('fk_donations_donation_request_id_donationrequest')),
    sa.ForeignKeyConstraint(['donor_id'], ['users.id'], name=op.f('fk_donations_donor_id_users')),
    sa.ForeignKeyConstraint(['ngo_id'], ['users.id'], name=op.f('fk_donations_ngo_id_users')),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('donations')
    op.drop_table('donationrequest')
    op.drop_table('users')
    op.drop_table('categories')
    # ### end Alembic commands ###
