# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for the package services."""

import pytest
from flask_principal import Identity
from invenio_access.permissions import any_user
from invenio_rdm_records.proxies import current_rdm_records_service

from geo_rdm_records.modules.resources import GEODraft, GEORecord


@pytest.fixture(scope="function")
def draft_resource_record(running_app, minimal_record):
    """Resource Record (Draft) fixture."""
    superuser_identity = running_app.superuser_identity

    record_item = current_rdm_records_service.create(superuser_identity, minimal_record)

    record_item = record_item.to_dict()
    record_pid = record_item["id"]

    return GEODraft.pid.resolve(record_pid, registered_only=False)


@pytest.fixture(scope="function")
def published_resource_record(running_app, minimal_record):
    """Resource Record (Published) fixture."""
    superuser_identity = running_app.superuser_identity

    record_item = current_rdm_records_service.create(superuser_identity, minimal_record)

    record_item = current_rdm_records_service.publish(
        superuser_identity, record_item.to_dict()["id"]
    )

    return GEORecord.pid.resolve(record_item.to_dict()["id"])


@pytest.fixture(scope="function")
def anyuser_identity():
    """System identity."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity
