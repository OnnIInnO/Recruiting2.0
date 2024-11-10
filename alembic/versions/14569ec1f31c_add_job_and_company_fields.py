"""add_job_and_company_fields

Revision ID: 14569ec1f31c
Revises: 509d1fbd1345
Create Date: 2024-11-10 02:38:53.353282

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "14569ec1f31c"
down_revision: Union[str, None] = "509d1fbd1345"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new columns
    op.add_column("companies", sa.Column("location", sa.String(), nullable=True))
    op.add_column("companies", sa.Column("logo_url", sa.String(), nullable=True))
    op.add_column("job_postings", sa.Column("salary_range", sa.String(), nullable=True))
    op.add_column(
        "job_postings", sa.Column("remote_policy", sa.String(), nullable=True)
    )
    op.add_column(
        "job_postings", sa.Column("application_deadline", sa.String(), nullable=True)
    )

    # Get references to the tables
    companies = sa.table(
        "companies", sa.column("location", sa.String), sa.column("logo_url", sa.String)
    )

    job_postings = sa.table(
        "job_postings",
        sa.column("salary_range", sa.String),
        sa.column("remote_policy", sa.String),
        sa.column("application_deadline", sa.String),
    )

    # Update existing records with default values
    op.execute(
        companies.update().values(
            {
                "location": "Helsinki, Finland",
                "logo_url": "https://via.placeholder.com/48",
            }
        )
    )

    op.execute(
        job_postings.update().values(
            {
                "salary_range": "$80k - $120k",
                "remote_policy": "Hybrid",
                "application_deadline": "2024-12-31",
            }
        )
    )


def downgrade():
    op.drop_column("job_postings", "application_deadline")
    op.drop_column("job_postings", "remote_policy")
    op.drop_column("job_postings", "salary_range")
    op.drop_column("companies", "logo_url")
    op.drop_column("companies", "location")
