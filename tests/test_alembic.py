# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test alembic recipes for GEO-RDM-Records."""

import pytest
from invenio_db.utils import alembic_test_context, drop_alembic_version_table


def test_alembic(base_app, database):
    """Test alembic recipes."""
    db = database
    ext = base_app.extensions["invenio-db"]

    if db.engine.name == "sqlite":
        raise pytest.skip("Upgrades are not supported on SQLite.")

    base_app.config["ALEMBIC_CONTEXT"] = alembic_test_context()

    # Check that this package's SQLAlchemy models have been properly registered
    tables = [x.name for x in db.get_tables_for_bind()]

    assert all(
        [
            x in tables
            for x in [
                "geo_package_parents_metadata",
                "geo_package_parents_community",
                "geo_package_records_metadata",
                "geo_package_records_files",
                "geo_package_drafts_metadata",
                "geo_package_drafts_files",
                "geo_package_versions_state",
                "geo_marketplace_parents_metadata",
                "geo_marketplace_parents_community",
                "geo_marketplace_items_metadata",
                "geo_marketplace_items_files",
                "geo_marketplace_drafts_metadata",
            ]
        ]
    )

    # Check that Alembic agrees that there's no further tables to create.
    assert not ext.alembic.compare_metadata()

    # Drop everything and recreate tables all with Alembic
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()
    assert not ext.alembic.compare_metadata()

    # Try to upgrade and downgrade
    ext.alembic.stamp()
    ext.alembic.downgrade(target="96e796392533")
    ext.alembic.upgrade()
    assert not ext.alembic.compare_metadata()

    drop_alembic_version_table()
