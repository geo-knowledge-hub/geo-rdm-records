# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Records API Services."""

from invenio_rdm_records.proxies import current_rdm_records_service


def test_resource_draft_creation(running_app, db, minimal_record, es_clear):
    """Test the creation of a package draft."""
    superuser_identity = running_app.superuser_identity

    # 1. Testing the draft creation.
    record_item = current_rdm_records_service.create(superuser_identity, minimal_record)

    # 2. Checking the generated package.
    record_item_dict = record_item.to_dict()

    assert record_item_dict.get("id") is not None


def test_resource_record_creation(running_app, db, minimal_record, es_clear):
    """Test the creation of a package record (Published)."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a draft.
    record_item = current_rdm_records_service.create(superuser_identity, minimal_record)

    # 2. Testing the draft publication.
    package_pid = record_item["id"]

    record_item_published = current_rdm_records_service.publish(
        superuser_identity, package_pid
    )

    # 3. Checking the generated package.
    record_item_published_dict = record_item_published.to_dict()

    assert record_item_published_dict.get("id") is not None
