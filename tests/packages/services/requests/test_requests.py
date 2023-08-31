# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Requests Service for packages."""

import pytest
from invenio_requests import current_requests_service

from geo_rdm_records.proxies import current_geo_packages_service


#
# Tests
#
def test_simple_flow(running_app, refresh_index, published_package):
    """Test simple usage workflow for package requests."""
    # Creating request
    package_id = published_package["id"]

    request = current_geo_packages_service.request.update(
        running_app.superuser_identity,
        package_id,
        {
            "topic": {"package_record": package_id},
            "type": "requests-assistance-training-creation",
        },
    )

    request = request.to_dict()

    # Validating request
    assert request["is_open"] is False
    assert request["status"] == "created"
    assert request["type"] == "requests-assistance-training-creation"
    assert "package_record" in request["topic"]

    # Submitting request
    request = current_geo_packages_service.request.submit(
        running_app.superuser_identity,
        package_id,
        {"payload": {"content": "This is a test", "format": "html"}},
    )

    request = request.to_dict()

    refresh_index()

    # Validating request
    assert request["status"] == "submitted"

    # Accepting request
    request = current_requests_service.execute_action(
        running_app.superuser_identity, request["id"], "accept", {}
    ).to_dict()

    assert request["status"] == "accepted"
    assert request["is_open"] is False
