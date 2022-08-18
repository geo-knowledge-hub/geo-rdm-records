# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Resources."""

import json

import arrow

from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)
from geo_rdm_records.modules.resources.records.api import GEODraft, GEORecord


#
# Auxiliary functions
#
def _assert_single_item_response(response):
    """Assert the fields present on a single item response."""
    response_fields = response.json.keys()
    fields_to_check = ["access", "created", "id", "links", "metadata", "updated"]

    for field in fields_to_check:
        assert field in response_fields


def _validate_access(response, original):
    """Validate that the record's access is as specified."""
    assert "access" in response

    access, orig_access = response["access"], original["access"]
    assert access["record"] == orig_access["record"]
    assert access["files"] == orig_access["files"]

    if orig_access.get("embargo"):
        assert "embargo" in access
        embargo, orig_embargo = access["embargo"], orig_access["embargo"]

        until = arrow.get(embargo["until"]).datetime
        orig_until = arrow.get(orig_embargo["until"]).datetime
        assert until.isoformat() == orig_until.isoformat()

        if embargo.get("reason"):
            assert embargo.get("reason") == orig_embargo.get("reason")

        assert embargo.get("active") == orig_embargo.get("active")


#
# Tests
#
def test_package_deposit_flow(
    running_app, client_with_login, minimal_record, headers, es_clear
):
    """Simple Package REST API deposit flow."""
    base_url = "/packages"
    client = client_with_login

    # Creating a draft
    created_draft = client.post(
        base_url, headers=headers, data=json.dumps(minimal_record)
    )
    assert created_draft.status_code == 201
    _assert_single_item_response(created_draft)
    _validate_access(created_draft.json, minimal_record)
    id_ = created_draft.json["id"]

    # Reading the draft
    read_draft = client.get(f"{base_url}/{id_}/draft", headers=headers)

    assert read_draft.status_code == 200
    assert read_draft.json["metadata"] == created_draft.json["metadata"]
    _validate_access(read_draft.json, minimal_record)

    # Updating the draft
    data = read_draft.json
    data["metadata"]["title"] = "New title"

    res = client.put(f"{base_url}/{id_}/draft", headers=headers, data=json.dumps(data))

    assert res.status_code == 200
    assert res.json["metadata"]["title"] == "New title"
    _validate_access(res.json, minimal_record)

    # Publishing the created draft
    response = client.post(f"{base_url}/{id_}/draft/actions/publish", headers=headers)

    # Checking if the record was created
    assert response.status_code == 202

    recid = response.json["id"]
    response = client.get(f"{base_url}/{recid}", headers=headers)

    assert response.status_code == 200
    _validate_access(response.json, minimal_record)

    # Refreshing the index before search for records
    GEOPackageRecord.index.refresh()

    # Searching for the published package
    created_record = response.json

    res = client.get(f"{base_url}", query_string={"q": f"id:{recid}"}, headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["metadata"] == created_record["metadata"]

    data = res.json["hits"]["hits"][0]

    assert data["metadata"]["title"] == "New title"
    _validate_access(data, minimal_record)


def test_package_resource_integration_flow(
    running_app,
    client_with_login,
    minimal_record,
    draft_record,
    published_record,
    headers,
    es_clear
):
    """Test Packages and resources integration flow."""
    package_base_url = "/packages"

    client = client_with_login

    # Auxiliary functions
    def _refresh_index():
        GEOPackageDraft.index.refresh()
        GEODraft.index.refresh()
        GEORecord.index.refresh()

    # 1. Creating a package
    created_draft = client.post(
        package_base_url, headers=headers, data=json.dumps(minimal_record)
    )

    # 2. Linking resources in the package
    created_draft_id = created_draft.json["id"]

    package_resources_url = f"{package_base_url}/{created_draft_id}/draft/resources"
    resources = dict(
        resources=[
            {"id": draft_record, "type": "managed"},
            {"id": published_record, "type": "related"},
        ]
    )

    response = client.post(
        package_resources_url, headers=headers, data=json.dumps(resources)
    )

    assert response.status_code == 204

    # Refreshing indices
    _refresh_index()

    # 3. Checking if the `Managed` record are associated with the package
    response = client.get(package_resources_url, headers=headers)

    assert response.status_code == 200
    assert response.json["hits"]["total"] == 1

    # 4. Checking if the `Related` record are associated with the package
    package_url = f"{package_base_url}/{created_draft_id}/draft"

    response = client.get(package_url, headers=headers)

    assert response.status_code == 200

    # 4.1. Validating the content
    relationship = response.json["relationship"]

    assert len(relationship["related_resources"]) == 1
    assert relationship["managed_resources"][0]["id"] == draft_record
    assert relationship["related_resources"][0]["id"] == published_record

    # 5. Removing resources from the package

    # 5.1. Removing the `Managed` records
    managed_resources = dict(
        resources=[
            {"id": draft_record, "type": "managed"},
        ]
    )

    # 5.1.1. Removing
    response = client.delete(
        package_resources_url, headers=headers, data=json.dumps(managed_resources)
    )

    assert response.status_code == 204

    # Refreshing indices
    _refresh_index()

    # 5.1.2. Checking if the record was removed using the package document
    response = client.get(package_url, headers=headers)

    assert response.status_code == 200
    assert len(response.json["relationship"]["managed_resources"]) == 0

    # 5.1.3. Checking if the record was removing using the search method
    response = client.get(package_resources_url, headers=headers)

    assert response.status_code == 200
    assert response.json["hits"]["total"] == 0

    # 5.2. Removing the `Related` records
    related_resources = dict(
        resources=[
            {"id": published_record, "type": "related"},
        ]
    )

    # 5.2.1. Removing
    response = client.delete(
        package_resources_url, headers=headers, data=json.dumps(related_resources)
    )

    assert response.status_code == 204

    # Refreshing indices
    _refresh_index()

    # 5.2.2. Checking if the record was removed using the package document
    response = client.get(package_url, headers=headers)

    assert response.status_code == 200
    assert len(response.json["relationship"]["related_resources"]) == 0
