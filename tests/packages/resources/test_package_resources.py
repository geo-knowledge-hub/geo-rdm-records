# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Resources."""

import json

import arrow
import pytest

from geo_rdm_records.modules.packages.records.api import GEOPackageRecord


@pytest.fixture()
def ui_headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/vnd.inveniordm.v1+json",
    }


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


def test_package_deposit_flow(
    running_app, client_with_login, minimal_record, headers, es_clear
):
    """Simple Package REST API deposit flow."""
    base_url = "/packages"
    client = client_with_login

    # Create a draft
    created_draft = client.post(
        base_url, headers=headers, data=json.dumps(minimal_record)
    )
    assert created_draft.status_code == 201
    _assert_single_item_response(created_draft)
    _validate_access(created_draft.json, minimal_record)
    id_ = created_draft.json["id"]

    # Read the draft
    read_draft = client.get(f"{base_url}/{id_}/draft", headers=headers)
    assert read_draft.status_code == 200
    assert read_draft.json["metadata"] == created_draft.json["metadata"]
    _validate_access(read_draft.json, minimal_record)

    # Update and save draft
    data = read_draft.json
    data["metadata"]["title"] = "New title"

    res = client.put(f"{base_url}/{id_}/draft", headers=headers, data=json.dumps(data))
    assert res.status_code == 200
    assert res.json["metadata"]["title"] == "New title"
    _validate_access(res.json, minimal_record)

    # Publish it
    response = client.post(f"{base_url}/{id_}/draft/actions/publish", headers=headers)

    # Check record was created
    assert response.status_code == 202

    recid = response.json["id"]
    response = client.get(f"{base_url}/{recid}", headers=headers)

    assert response.status_code == 200
    _validate_access(response.json, minimal_record)

    created_record = response.json

    GEOPackageRecord.index.refresh()

    # Search it
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
):
    """Test Packages and resources integration flow."""
    base_url = "/packages"
    client = client_with_login

    # 1. Creating a package
    created_draft = client.post(
        base_url, headers=headers, data=json.dumps(minimal_record)
    )
    created_draft_id = created_draft.json["id"]

    # 2. Linking the resources in the package.
    resources_url = f"{base_url}/{created_draft_id}/draft/resources"

    resources = dict(
        resources=[
            {"id": draft_record, "type": "managed"},
            {"id": published_record, "type": "related"},
        ]
    )

    response = client.post(resources_url, headers=headers, data=json.dumps(resources))
    assert response.status_code == 204

    # 3. Removing resources from the package.
    response = client.delete(resources_url, headers=headers, data=json.dumps(resources))
    assert response.status_code == 204
