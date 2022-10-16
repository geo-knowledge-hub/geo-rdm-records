# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Resources."""

import json

import pytest

from geo_rdm_records.customizations.records.api import GEODraft, GEORecord


@pytest.fixture()
def package(running_app, client_with_login, minimal_package, headers):
    """Get the current RDM records service."""
    base_url = "/packages"
    client = client_with_login

    created_draft = client.post(
        base_url, headers=headers, data=json.dumps(minimal_package)
    )

    return created_draft.json["id"]


def test_search_package_records(
    running_app, client_with_login, minimal_record, headers, package, es_clear
):
    """Test searching for records in a package."""
    base_records_url = "/records"
    base_package_url = "/packages"
    client = client_with_login

    def _create_and_include_in_package():
        # Create a draft
        created_draft = client.post(
            base_records_url, headers=headers, data=json.dumps(minimal_record)
        )

        elements = [
            {"id": created_draft.json["id"]},
        ]

        # Associating resources into the package.
        records = dict(records=elements)

        context_url = f"{base_package_url}/{package}/context/actions/associate"
        client.post(context_url, headers=headers, data=json.dumps(records))

        # Adding resource into a specific package version
        resources = dict(resources=elements)

        resources_url = f"{base_package_url}/{package}/draft/resources"
        client.post(resources_url, headers=headers, data=json.dumps(resources))

        # Refreshing the index.
        GEODraft.index.refresh()
        GEORecord.index.refresh()

    # Base record api test.
    res = client.get(base_records_url)
    assert res.status_code == 200

    # Searching an empty package.
    res = client.get(f"{base_package_url}/{package}/draft/resources", headers=headers)
    assert res.json["hits"]["total"] == 0

    _create_and_include_in_package()

    # Searching for a filled packaged.
    res = client.get(f"{base_package_url}/{package}/draft/resources", headers=headers)
    assert res.json["hits"]["total"] == 1
