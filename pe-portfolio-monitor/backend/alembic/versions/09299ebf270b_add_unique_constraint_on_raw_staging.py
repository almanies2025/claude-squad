"""add unique constraint on raw_staging for upsert

Revision ID: 09299ebf270b
Revises: 001_initial_schema
Create Date: 2026-04-20 18:37:38.745028

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "09299ebf270b"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_raw_staging_company_period_account",
        "raw_staging",
        ["company_id", "period_id", "source_account_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_raw_staging_company_period_account",
        "raw_staging",
        type_="unique",
    )
