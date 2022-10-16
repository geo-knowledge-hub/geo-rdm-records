# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Review Service for packages."""

import pytest
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_requests import current_requests_service
from sqlalchemy.orm.exc import NoResultFound

from geo_rdm_records.proxies import current_geo_packages_service


@pytest.fixture()
def service():
    """Get the current GEO RDM Records service."""
    return current_geo_packages_service


@pytest.fixture()
def resources_service():
    """Get the current Invenio RDM Records service."""
    return current_rdm_records_service


@pytest.fixture()
def requests_service():
    """Get the current RDM records service."""
    return current_requests_service


@pytest.fixture()
def draft(minimal_package, community_record, service, running_app, db):
    minimal_package["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": community_record.id},
        }
    }

    # Create draft with review
    return service.create(running_app.superuser_identity, minimal_package)


#
# Tests
#
def test_package_reviewing_validation(
    running_app,
    community_record,
    service,
    resources_service,
    minimal_package,
    minimal_record,
    requests_service,
    es_clear,
):
    """Test the package reviewing flow."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package
    package = service.create(superuser_identity, minimal_package)
    package_id = package["id"]

    # 2. Create a resource
    resource = resources_service.create(superuser_identity, minimal_record)
    resource_id = resource["id"]

    # 3. Linking the package in the resource
    elements = [{"id": resource_id}]

    records = dict(records=elements)
    resources = dict(resources=elements)

    service.context_associate(superuser_identity, package_id, records)
    service.resource_add(superuser_identity, package_id, resources)

    # 4. Trying to link the package with a community

    # 4.1. Adding valid modification
    review_definition = dict(
        type="community-submission", receiver={"community": community_record.id}
    )

    # 4.2. Creating the review for the package
    req = service.review.update(superuser_identity, package_id, review_definition)

    assert req["status"] == "created"

    # 5. Submitting the review
    req = service.review.submit(superuser_identity, package_id).to_dict()

    # 6. Accepting the request (the package must be part of the community)
    req = requests_service.execute_action(
        superuser_identity, req["id"], "accept", {}
    ).to_dict()

    assert req["status"] == "accepted"
    assert req["is_open"] is False

    # 5. Checking if the record's status was updated correctly

    # 5.1. Reading the record and checking basic publishing properties
    record = service.read(running_app.superuser_identity, package_id).to_dict()

    assert "review" not in record["parent"]
    assert record["is_published"] is True

    # 5.2. Validating the communities properties
    community_record_id = str(community_record.id)

    assert record["parent"]["communities"]["ids"] == [community_record_id]
    assert record["parent"]["communities"]["default"] == community_record_id
    assert record["status"] == "published"

    # 5.3. Trying to read the draft (which should have been removed)
    with pytest.raises(NoResultFound):
        service.read_draft(running_app.superuser_identity, package_id)

    # 6. Creating a new version of the record (must be part of the community)
    draft = service.new_version(running_app.superuser_identity, package_id).to_dict()

    assert "review" not in draft["parent"]
    assert draft["parent"]["communities"]["ids"] == [community_record_id]
    assert draft["parent"]["communities"]["default"] == community_record_id
    assert draft["status"] == "new_version_draft"

    # 7. Checking the package resources (`Managed` resources)
    record_relationship_managed = record["relationship"]["resources"]

    for record_resource in record_relationship_managed:
        # reading resource metadata
        record_resource_id = record_resource["id"]

        record_resource_obj = resources_service.read(
            superuser_identity, record_resource_id
        ).to_dict()

        if (
            record_resource_obj["parent"]["relationship"]["managed_by"]["id"]
            == record["parent"]["id"]
        ):
            assert record_resource_obj["is_draft"] is False
            assert record_resource_obj["is_published"] is True

            # Package resources must be associated with the community
            assert (
                record_resource_obj["parent"]["communities"]["ids"]
                == record["parent"]["communities"]["ids"]
            )
