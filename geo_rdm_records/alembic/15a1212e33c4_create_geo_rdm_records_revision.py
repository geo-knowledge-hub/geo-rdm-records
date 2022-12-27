# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create geo-rdm-records revision."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "15a1212e33c4"
down_revision = None
branch_labels = ("geo_rdm_records",)
depends_on = "dbdbc1b19cf2"


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
