# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Services."""

from contextlib import nullcontext as does_not_raise

from geo_rdm_records.modules.packages import GEOPackageDraft
from geo_rdm_records.proxies import current_geo_packages_service


def test_minimal_draft_creation(running_app, es_clear, minimal_record):
    superuser_identity = running_app.superuser_identity

    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_record
    )
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["resource_type"] == {
        "id": "image-photo",
        "title": {"en": "Photo"},
    }


def test_draft_w_languages_creation(running_app, es_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    minimal_record["metadata"]["languages"] = [
        {
            "id": "eng",
        }
    ]

    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_record
    )
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["languages"] == [
        {"id": "eng", "title": {"en": "English", "da": "Engelsk"}}
    ]


def test_package_resource_integration_service(
    running_app, db, draft_record, published_record, minimal_record
):
    """Basic smoke test for the package integration service."""
    superuser_identity = running_app.superuser_identity

    # creating the package
    package_draft = GEOPackageDraft.create(minimal_record)
    package_pid = package_draft.pid.pid_value

    resources = dict(
        resources=[
            {"id": draft_record.pid.pid_value, "type": "managed"},
            {"id": published_record.pid.pid_value, "type": "related"},
        ]
    )

    # 1. Testing the ``add`` operation.
    with does_not_raise():
        current_geo_packages_service.resource_add(
            superuser_identity, package_pid, resources
        )

    # loading the package updated
    package_draft = GEOPackageDraft.pid.resolve(package_pid, registered_only=False)

    assert len(package_draft.relationship.managed) == 1
    assert len(package_draft.relationship.related) == 1

    # 2. Testing the ``delete`` operation.
    resources_to_be_deleted = dict(
        resources=[{"id": draft_record.pid.pid_value, "type": "managed"}]
    )

    with does_not_raise():
        current_geo_packages_service.resource_delete(
            superuser_identity, package_pid, resources_to_be_deleted
        )

    # loading the package updated
    package_draft = GEOPackageDraft.pid.resolve(package_pid, registered_only=False)

    assert len(package_draft.relationship.managed) == 0
    assert len(package_draft.relationship.related) == 1

    # 3. Testing the ``update`` operation.
    resources_to_be_updated = dict(
        resources=[
            {"id": published_record.pid.pid_value, "type": "related"},
        ]
    )

    with does_not_raise():
        # ToDo: if the base rules continue with the current approach,
        #       the updated method will not be required anymore.
        current_geo_packages_service.resource_update(
            superuser_identity, package_pid, resources_to_be_updated
        )

    # loading the package updated
    package_draft = GEOPackageDraft.pid.resolve(package_pid, registered_only=False)

    assert len(package_draft.relationship.managed) == 0
    assert len(package_draft.relationship.related) == 1
