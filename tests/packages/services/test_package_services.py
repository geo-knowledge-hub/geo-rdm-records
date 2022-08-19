# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Services."""

from invenio_rdm_records.proxies import current_rdm_records_service

from geo_rdm_records.modules.packages import GEOPackageDraft
from geo_rdm_records.proxies import current_geo_packages_service


def test_package_draft_creation(running_app, db, minimal_record, es_clear):
    """Test the creation of a package draft."""
    superuser_identity = running_app.superuser_identity

    # 1. Testing the draft creation.
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_record
    )

    # 2. Checking the generated package.
    record_item_dict = record_item.to_dict()

    assert record_item_dict.get("id") is not None


def test_package_record_creation(running_app, db, minimal_record, es_clear):
    """Test the creation of a package record (Published)."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating the draft.
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_record
    )

    # 2. Testing the draft publication.
    package_pid = record_item["id"]

    record_item_published = current_geo_packages_service.publish(
        superuser_identity, package_pid
    )

    # 3. Checking the generated package.
    record_item_published_dict = record_item_published.to_dict()

    assert record_item_published_dict.get("id") is not None


def test_package_resource_integration_service(
    running_app, db, draft_resource_record, published_resource_record, minimal_record
):
    """Basic smoke test for the package integration service."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    package_draft = GEOPackageDraft.create(minimal_record)
    package_draft.commit()

    db.session.commit()
    GEOPackageDraft.index.refresh()

    package_pid = package_draft.pid.pid_value

    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value, "type": "managed"},
            {"id": published_resource_record.pid.pid_value, "type": "related"},
        ]
    )

    # 2. Testing the ``add resource`` operation.
    current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )

    # loading the package updated
    package_draft = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    )

    package_draft_relationship = package_draft["relationship"]

    # verifying the basic structure of the ``relationship``
    assert package_draft_relationship is not None
    assert len(package_draft_relationship.keys()) == 2
    assert len(package_draft_relationship["managed_resources"]) == 1
    assert len(package_draft_relationship["related_resources"]) == 1

    # checking the ``relationship`` content
    managed_resources = [
        i for i in package_draft_relationship["managed_resources"] if i
    ]
    related_resources = [
        i for i in package_draft_relationship["related_resources"] if i
    ]

    assert len(managed_resources) == 1
    assert len(related_resources) == 1

    # 3. Testing the ``delete resource`` operation.
    resources_to_be_deleted = dict(
        resources=[{"id": draft_resource_record.pid.pid_value, "type": "managed"}]
    )

    current_geo_packages_service.resource_delete(
        superuser_identity, package_pid, resources_to_be_deleted
    )

    # loading the package updated
    package_draft = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    )

    package_draft_relationship = package_draft["relationship"]

    assert len(package_draft_relationship.keys()) == 2
    assert len(package_draft_relationship["managed_resources"]) == 0
    assert len(package_draft_relationship["related_resources"]) == 1


def test_package_publishing_workflow(
    running_app,
    db,
    draft_resource_record,
    published_resource_record,
    minimal_record,
    refresh_index,
    es_clear,
):
    """Basic smoke test for the package publishing workflow."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_record
    )

    package_pid = record_item["id"]

    # 2. Add resources to the package.
    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value, "type": "managed"},
            {"id": published_resource_record.pid.pid_value, "type": "related"},
        ]
    )

    current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )

    # refreshing the index
    refresh_index()

    # 3. Searching for published resource records
    package_records = current_rdm_records_service.search_package_records(
        superuser_identity, package_pid
    )
    package_records = package_records.to_dict()

    assert package_records["hits"]["total"] == 0

    # 4. Publishing the package updated
    record_item_published = current_geo_packages_service.publish(
        superuser_identity, package_pid
    )

    # 5. Checking the generated package.
    assert record_item_published["id"] is not None

    # refreshing the index
    refresh_index()

    # 6. Searching for published resource records
    package_records = current_rdm_records_service.search_package_records(
        superuser_identity, package_pid
    )
    package_records = package_records.to_dict()

    assert (
        package_records["hits"]["total"] == 1
    )  # we are able to search for published records.
