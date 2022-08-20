# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Review Service."""

import pytest
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.systemfields.draft_status import DraftStatus
from invenio_requests import current_requests_service
from sqlalchemy.orm.exc import NoResultFound

from geo_rdm_records.modules.resources.services.review.errors import (
    ReviewInconsistentResourceRestrictions,
)
from geo_rdm_records.proxies import current_geo_packages_service


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records.records_service


@pytest.fixture()
def packages_service():
    """Get the current GEO RDM Records Packages services."""
    return current_geo_packages_service


@pytest.fixture()
def requests_service():
    """Get the current RDM records service."""
    return current_requests_service


@pytest.fixture()
def draft(minimal_record, community_record, service, running_app, db):
    minimal_record["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": community_record.id},
        }
    }

    # Create draft with review
    return service.create(running_app.superuser_identity, minimal_record)


#
# Tests
#
def test_package_resource_reviewing_validation(
    running_app,
    community_record,
    service,
    packages_service,
    minimal_record,
    es_clear,
):
    """Test the package resource relation in the reviewing flow."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package
    package = packages_service.create(superuser_identity, minimal_record)
    package_id = package["id"]

    # 2. Create a resource
    resource = service.create(superuser_identity, minimal_record)
    resource_id = resource["id"]

    # 3. Linking the package in the resource
    resources = dict(resources=[{"id": resource_id, "type": "managed"}])

    packages_service.resource_add(superuser_identity, package_id, resources)

    # 4. Trying to link the resource with a community

    # 4.1. Adding invalid modification
    review_definition = dict(
        type="community-submission", receiver={"community": community_record.id}
    )

    # 4.2. Updating the resource
    with pytest.raises(ReviewInconsistentResourceRestrictions):
        service.review.update(superuser_identity, resource_id, review_definition)


def test_simple_reviewing_flow(
    draft,
    running_app,
    community_record,
    service,
    requests_service,
    es_clear,
):
    """Test basic creation with review.

    Note:
        This test was adapted from ``Invenio RDM Records``. We are using it to make sure
        that the injected service (`RDM_REVIEW_SERVICE`) is working correctly.
    """
    # 1. Check draft status
    assert draft["status"] == DraftStatus.review_to_draft_statuses["created"]

    # 2. Submitting the already defined draft to revision (to be part of a community).
    req = service.review.submit(running_app.superuser_identity, draft.id).to_dict()

    assert req["status"] == "submitted"
    assert req["title"] == draft["metadata"]["title"]

    # 2.1. Checking the draft status
    draft = service.read_draft(running_app.superuser_identity, draft.id)

    assert (
        draft.to_dict()["status"] == DraftStatus.review_to_draft_statuses["submitted"]
    )

    # 3. Accepting the request/review (draft will be part of the community).
    req = requests_service.execute_action(
        running_app.superuser_identity, req["id"], "accept", {}
    ).to_dict()

    assert req["status"] == "accepted"
    assert req["is_open"] is False

    # 4. Checking if the record's status was updated correctly

    # 4.1. Reading the record and checking basic publishing properties
    record = service.read(running_app.superuser_identity, draft.id).to_dict()

    assert "review" not in record["parent"]
    assert record["is_published"] is True

    # 4.2. Validating the communities properties
    community_record_id = str(community_record.id)

    assert record["parent"]["communities"]["ids"] == [community_record_id]
    assert record["parent"]["communities"]["default"] == community_record_id
    assert record["status"] == "published"

    # 4.3. Trying to read the draft (which should have been removed)
    with pytest.raises(NoResultFound):
        service.read_draft(running_app.superuser_identity, draft.id)

    # 5. Creating a new version of the record (must be part of the community)
    draft = service.new_version(running_app.superuser_identity, draft.id).to_dict()

    assert "review" not in draft["parent"]
    assert draft["parent"]["communities"]["ids"] == [community_record_id]
    assert draft["parent"]["communities"]["default"] == community_record_id
    assert draft["status"] == "new_version_draft"
