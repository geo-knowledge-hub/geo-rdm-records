# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for the package services."""

import pytest

from geo_rdm_records.modules.packages.records.api import GEOPackageRecord
from geo_rdm_records.proxies import current_geo_packages_service


@pytest.fixture()
def published_package(running_app, minimal_package):
    """Published package fixture."""
    # Create draft
    package_draft = current_geo_packages_service.create(
        running_app.superuser_identity, minimal_package
    ).to_dict()
    package_draft_id = package_draft["id"]

    # Publish package
    package_published = current_geo_packages_service.publish(
        running_app.superuser_identity, package_draft_id
    ).to_dict()
    package_published_id = package_published["id"]

    return GEOPackageRecord.pid.resolve(package_published_id)
