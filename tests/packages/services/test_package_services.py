# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Services."""

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service
from sqlalchemy.orm.exc import NoResultFound

from geo_rdm_records.modules.packages import GEOPackageDraft
from geo_rdm_records.proxies import current_geo_packages_service


def test_package_draft_creation(running_app, db, minimal_package, es_clear):
    """Test the creation of a package draft."""
    superuser_identity = running_app.superuser_identity

    # 1. Testing the draft creation.
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    # 2. Checking the generated package.
    record_item_dict = record_item.to_dict()

    assert record_item_dict.get("id") is not None


def test_package_record_creation(running_app, db, minimal_package, es_clear):
    """Test the creation of a package record (Published)."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating the draft.
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    # 2. Testing the draft publication.
    package_pid = record_item["id"]

    record_item_published = current_geo_packages_service.publish(
        superuser_identity, package_pid
    )

    # 3. Checking the generated package.
    record_item_published_dict = record_item_published.to_dict()

    assert record_item_published_dict.get("id") is not None


def test_package_context(
    running_app, db, draft_resource_record, published_resource_record, minimal_package
):
    """Test Package context operations (Associate and Dissociate)."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    package_draft = GEOPackageDraft.create(minimal_package)
    package_draft.commit()

    db.session.commit()
    GEOPackageDraft.index.refresh()

    package_pid = package_draft.pid.pid_value
    package_parent_pid = package_draft.parent.pid.pid_value

    # 2. Associating record with the package context
    records = dict(
        records=[
            {"id": draft_resource_record.pid.pid_value},
            {"id": published_resource_record.pid.pid_value},
        ]
    )

    current_geo_packages_service.context_associate(
        superuser_identity, package_pid, records
    )

    # Checking if the association is working
    for resource, draft in [
        (draft_resource_record, True),
        (published_resource_record, False),
    ]:
        method_ = current_rdm_records_service.read_draft
        if not draft:
            method_ = current_rdm_records_service.read

        resource = method_(superuser_identity, resource.pid.pid_value).to_dict()

        assert (
            resource["parent"]["relationship"]["managed_by"]["id"] == package_parent_pid
        )

    # Checking if the specific version of the package was not changed
    package_changed = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    ).to_dict()

    assert "relationship" in package_changed
    assert len(package_changed["relationship"]["resources"]) == 0

    # 3. Dissociating record from the package context
    records = dict(
        records=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    current_geo_packages_service.context_dissociate(
        superuser_identity, package_pid, records
    )

    # Checking if dissociation is working
    resource = current_rdm_records_service.read_draft(
        superuser_identity, draft_resource_record.pid.pid_value
    )

    assert len(resource["parent"]["relationship"].keys()) == 0

    # ToDo: Entrypoint to get general information from the context
    # {users, resources, ...}


def test_package_resource_integration_service(
    running_app, db, draft_resource_record, published_resource_record, minimal_package
):
    """Basic smoke test for the package integration service."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    package_draft = GEOPackageDraft.create(minimal_package)
    package_draft.commit()

    db.session.commit()
    GEOPackageDraft.index.refresh()

    package_pid = package_draft.pid.pid_value

    # 2. Testing the ``add resource`` operation.
    # 2.1. Draft can only be associated if already defined inside the
    #      package context

    # Test 1 (Draft out package context)
    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )

    assert len(result["errors"]) != 0

    # Test 2 (Published record out package context)
    resources = dict(
        resources=[
            {"id": published_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )

    assert len(result["errors"]) == 0

    # checking the package updated
    package_draft = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    )

    package_draft_relationship = package_draft["relationship"]

    # verifying the basic structure of the ``relationship``
    assert package_draft_relationship is not None
    assert len(package_draft_relationship.keys()) == 1
    assert len(package_draft_relationship["resources"]) == 1

    # checking the resource updated
    resource_updated = current_rdm_records_service.read(
        superuser_identity, published_resource_record.pid.pid_value
    )

    resource_updated_relationship = resource_updated["relationship"]

    # verifying the basic structure of the ``relationship``
    assert resource_updated_relationship is not None
    assert len(resource_updated_relationship.keys()) == 1
    assert len(resource_updated_relationship["packages"]) == 1

    # Test 3 (Draft out package context)
    # Associating the resource with package context
    records = dict(
        records=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    current_geo_packages_service.context_associate(
        superuser_identity, package_pid, records
    )

    # Adding draft in the package
    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )
    assert len(result["errors"]) == 0

    # checking the package updated
    package_draft = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    )

    package_draft_relationship = package_draft["relationship"]

    # verifying the basic structure of the ``relationship``
    assert package_draft_relationship is not None
    assert len(package_draft_relationship.keys()) == 1
    assert len(package_draft_relationship["resources"]) == 2

    # checking the resource updated
    resource_updated = current_rdm_records_service.read_draft(
        superuser_identity, draft_resource_record.pid.pid_value
    )

    resource_updated_relationship = resource_updated["relationship"]

    # verifying the basic structure of the ``relationship``
    assert resource_updated_relationship is not None
    assert len(resource_updated_relationship.keys()) == 1
    assert len(resource_updated_relationship["packages"]) == 1

    # 3. Testing the ``delete resource`` operation.
    resources_to_be_deleted = dict(
        resources=[{"id": draft_resource_record.pid.pid_value}]
    )

    current_geo_packages_service.resource_delete(
        superuser_identity, package_pid, resources_to_be_deleted
    )

    # checking the package updated
    package_draft = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    )

    package_draft_relationship = package_draft["relationship"]

    assert len(package_draft_relationship.keys()) == 1
    assert len(package_draft_relationship["resources"]) == 1

    # checking the resource updated
    resource_updated = current_rdm_records_service.read_draft(
        superuser_identity, draft_resource_record.pid.pid_value
    )

    resource_updated_relationship = resource_updated["relationship"]

    # verifying the basic structure of the ``relationship``
    assert resource_updated_relationship is not None
    assert len(resource_updated_relationship.keys()) == 1
    assert len(resource_updated_relationship["packages"]) == 0


def test_package_publishing_flow(
    running_app,
    db,
    draft_resource_record,
    published_resource_record,
    minimal_package,
    refresh_index,
    es_clear,
):
    """Basic smoke test for the package publishing workflow."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    package_pid = record_item["id"]

    # 2. Add resources to the package.
    # 2.1. Associating the draft resource with package context
    records = dict(
        records=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    current_geo_packages_service.context_associate(
        superuser_identity, package_pid, records
    )

    # 2.2. Adding the resources to the specific version of the package
    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value},
            {"id": published_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )
    assert len(result["errors"]) == 0

    # refreshing the index
    refresh_index()

    # 3. Searching for published resource records
    package_records = current_rdm_records_service.search_package_records(
        superuser_identity, package_pid
    )
    package_records = package_records.to_dict()

    assert package_records["hits"]["total"] == 1

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
        package_records["hits"]["total"] == 2
    )  # we are able to search for published records.


def test_package_edition_flow(
    running_app,
    db,
    draft_resource_record,
    published_resource_record,
    minimal_package,
    refresh_index,
    es_clear,
):
    """Test the edition flow for Packages and their resources."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    package_pid = record_item["id"]

    # 2. Add resources to the package.
    records = dict(
        records=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    current_geo_packages_service.context_associate(
        superuser_identity, package_pid, records
    )

    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value},
            {"id": published_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )
    assert len(result["errors"]) == 0

    # 3. Publishing the package updated
    current_geo_packages_service.publish(superuser_identity, package_pid)

    # refreshing the index
    refresh_index()

    # 4. Creating a draft from the published package (Edit mode)
    new_title = "The cake is a lie"

    draft_from_published_record = current_geo_packages_service.edit(
        superuser_identity, package_pid
    ).to_dict()

    assert draft_from_published_record["id"] == package_pid
    assert draft_from_published_record["metadata"]["title"] != new_title  # making sure

    # 5. Changing the draft

    # 5.1. Valid modification
    draft_from_published_record["metadata"]["title"] = new_title

    # 5.2. Invalid modification
    draft_from_published_record["relationship"] = {}  # trying to flush the content

    current_geo_packages_service.update_draft(
        superuser_identity, package_pid, draft_from_published_record
    )

    # refreshing the index
    refresh_index()

    # 6. Reloading and validating the modification
    published_record = current_geo_packages_service.read(
        superuser_identity, package_pid
    )
    draft_from_published_record = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    )

    # basic validation
    assert draft_from_published_record["metadata"]["title"] == new_title  # new title!
    assert (
        published_record["metadata"]["title"]
        != draft_from_published_record["metadata"]["title"]
    )

    # invalid modification don't change anything
    assert (
        draft_from_published_record["relationship"] == published_record["relationship"]
    )

    # 7. Publishing the draft
    current_geo_packages_service.publish(superuser_identity, package_pid)

    # 8. Loading and checking
    published_record = current_geo_packages_service.read(
        superuser_identity, package_pid
    )

    assert published_record["metadata"]["title"] == new_title

    # 9. Trying to load the draft again
    with pytest.raises(NoResultFound):
        current_geo_packages_service.read_draft(superuser_identity, package_pid)


def test_package_delete_resource_flow(
    running_app,
    db,
    draft_resource_record,
    published_resource_record,
    minimal_package,
    refresh_index,
    es_clear,
):
    """Test the resource deletion flow for Packages."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    package_pid = record_item["id"]
    resource_draft_pid = draft_resource_record.pid.pid_value

    # 2. Add resources to the package.
    records = dict(
        records=[
            {"id": resource_draft_pid},
        ]
    )

    current_geo_packages_service.context_associate(
        superuser_identity, package_pid, records
    )

    resources = dict(
        resources=[
            {"id": resource_draft_pid},
            {"id": published_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )
    assert len(result["errors"]) == 0

    # refreshing the index
    refresh_index()

    # 3. Delete the draft resource

    # 3.1. Testing package before delete the resource draft
    package_w_draft = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    ).to_dict()
    package_relationship = package_w_draft.get("relationship").get("resources")
    package_relationship = list(map(lambda x: x["id"], package_relationship))

    assert resource_draft_pid in package_relationship

    # 3.2. Deleting the resource draft

    # deleting draft resource
    current_rdm_records_service.delete_draft(superuser_identity, resource_draft_pid)

    # refreshing the index
    refresh_index()

    package_without_draft = current_geo_packages_service.read_draft(
        superuser_identity, package_pid
    ).to_dict()
    package_relationship = package_without_draft.get("relationship").get("resources")
    package_relationship = list(map(lambda x: x["id"], package_relationship))

    assert resource_draft_pid not in package_relationship

    # 4. Trying to load the resource draft
    with pytest.raises(PIDDoesNotExistError):
        current_rdm_records_service.read_draft(superuser_identity, resource_draft_pid)


def test_package_versioning_flow(
    running_app,
    db,
    draft_resource_record,
    published_resource_record,
    minimal_package,
    refresh_index,
    es_clear,
):
    """Test the ``import_resource`` operation from the Package service."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    package_pid = record_item["id"]

    # 2. Add resources to the package.
    records = dict(
        records=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    current_geo_packages_service.context_associate(
        superuser_identity, package_pid, records
    )

    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value},
            {"id": published_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )
    assert len(result["errors"]) == 0

    # 3. Publishing the package updated
    current_geo_packages_service.publish(superuser_identity, package_pid)

    # refreshing the index
    refresh_index()

    # 4. Creating a new package version.
    package_new_version = current_geo_packages_service.new_version(
        superuser_identity, package_pid
    )
    package_new_version = package_new_version.to_dict()

    package_new_pid = package_new_version["id"]

    # 5. Checking the resources
    package_new_relationship = package_new_version.get("relationship")

    assert len(package_new_relationship.get("resources", [])) == 0

    # 6. Importing resources from the previous version
    current_geo_packages_service.import_resources(superuser_identity, package_new_pid)

    # refreshing the index
    refresh_index()

    # 7. Checking for resources
    package_new_version = current_geo_packages_service.read_draft(
        superuser_identity, package_new_pid
    )
    package_new_version = package_new_version.to_dict()

    package_new_relationship = package_new_version.get("relationship")

    assert len(package_new_relationship.get("resources", [])) == 2

    # 8. Checking if the reference to the package was registered
    # in the resources side.
    resources = current_rdm_records_service.search_package_records(
        superuser_identity, package_new_pid
    )

    assert resources.total == 2


def test_update_package_access(
    running_app,
    db,
    draft_resource_record,
    published_resource_record,
    minimal_package,
    refresh_index,
    es_clear,
):
    """Test access (parent) update operation."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    # 2. Checking the access object
    package_pid = record_item["id"]
    package_obj = GEOPackageDraft.pid.resolve(package_pid, registered_only=False)

    assert package_obj.parent["access"]["record_policy"] == "open"

    # 3. Changing the record policy
    record_policy = dict(access={"record_policy": "closed"})

    current_geo_packages_service.context_update(
        superuser_identity, package_pid, record_policy
    )

    # refreshing the index
    refresh_index()

    # 4. Checking changed package
    package_obj = GEOPackageDraft.pid.resolve(package_pid, registered_only=False)

    assert package_obj.parent["access"]["record_policy"] == "closed"


def test_package_validation(
    running_app,
    db,
    draft_resource_record,
    published_resource_record,
    minimal_package,
    refresh_index,
    es_clear,
):
    """Test ``Validation`` operation."""
    superuser_identity = running_app.superuser_identity

    # 1. Creating a package draft
    record_item = current_geo_packages_service.create(
        superuser_identity, minimal_package
    )

    package_pid = record_item["id"]

    # 2. Add resources to the package.
    records = dict(
        records=[
            {"id": draft_resource_record.pid.pid_value},
        ]
    )

    current_geo_packages_service.context_associate(
        superuser_identity, package_pid, records
    )

    resources = dict(
        resources=[
            {"id": draft_resource_record.pid.pid_value},
            {"id": published_resource_record.pid.pid_value},
        ]
    )

    result = current_geo_packages_service.resource_add(
        superuser_identity, package_pid, resources
    )
    assert len(result["errors"]) == 0

    # 3. Validating
    result = current_geo_packages_service.validate_package(
        superuser_identity, package_pid
    )

    assert len(result["errors"]) == 0
