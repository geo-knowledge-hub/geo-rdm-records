# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest

from geo_rdm_records.modules.packages.records.api import GEOPackageDraft


@pytest.fixture()
def record_draft(app, db, minimal_record):
    """Record draft."""
    draft = GEOPackageDraft.create(minimal_record)
