# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package API Resources components."""

from contextlib import nullcontext as does_not_raise

import pytest
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.services.errors import PermissionDeniedError

from geo_rdm_records.modules.packages import GEOPackageDraft, GEOPackageRecord
from geo_rdm_records.modules.packages.errors import (
    InvalidPackageResourceError,
    InvalidRelationshipError,
)
from geo_rdm_records.modules.packages.records.api import PackageRelationship
from geo_rdm_records.modules.packages.services.components.resources.constraints import (
    CommunityRelationshipConstraint,
    PackageRelationshipConstraint,
    PublishedPackageConstraint,
    RecordStatusConstraint,
    ValidDraftConstraint,
)


def test_community_relationship_constraint(
    running_app, draft_record, published_record, community_record
):
    """Test the community relationship constraint."""
    superuser_identity = running_app.superuser_identity

    # 1. Draft without community is valid (For relationship equals to ``Related`` or ``Managed``).
    with does_not_raise():
        CommunityRelationshipConstraint.check(
            superuser_identity, draft_record, PackageRelationship.RELATED.value
        )

        CommunityRelationshipConstraint.check(
            superuser_identity, draft_record, PackageRelationship.MANAGED.value
        )

    # testing the constraint validation
    draft_record.parent.communities.add(community_record, default=True)
    draft_record.parent.commit()
    draft_record.commit()

    published_record.parent.communities.add(community_record, default=True)
    published_record.parent.commit()
    published_record.commit()

    # 2. Draft linked to a community is only valid when the relationship is ``Related``.
    with does_not_raise():
        CommunityRelationshipConstraint.check(
            superuser_identity, draft_record, PackageRelationship.RELATED.value
        )

        CommunityRelationshipConstraint.check(
            superuser_identity, published_record, PackageRelationship.RELATED.value
        )

    pytest.raises(
        InvalidPackageResourceError,
        CommunityRelationshipConstraint.check,
        identity=superuser_identity,
        record=draft_record,
        relationship_type=PackageRelationship.MANAGED.value,
    )


def test_valid_draft_constraint(
    running_app, anyuser_identity, draft_record, published_record
):
    """Test the Valid Draft constraint."""
    superuser_identity = running_app.superuser_identity

    # 1. Published record is valid
    with does_not_raise():
        ValidDraftConstraint.check(superuser_identity, published_record)

    # 2. User without permission to perform the ``update_draft`` action.
    pytest.raises(
        PermissionDeniedError,
        ValidDraftConstraint.check,
        identity=anyuser_identity,
        record=draft_record,
        service=current_rdm_records_service,
    )

    # 3. Invalid relationship
    pytest.raises(
        InvalidRelationshipError,
        ValidDraftConstraint.check,
        identity=superuser_identity,
        record=draft_record,
        relationship_type=PackageRelationship.RELATED.value,
        service=current_rdm_records_service,
    )

    # 4. Invalid record data
    draft_record["metadata"]["title"] = None

    pytest.raises(
        InvalidPackageResourceError,
        ValidDraftConstraint.check,
        identity=superuser_identity,
        record=draft_record,
        relationship_type=PackageRelationship.MANAGED.value,
        service=current_rdm_records_service,
    )


def test_record_status_constraint(
    running_app, anyuser_identity, draft_record, published_record
):
    """Test the Record Status constraint."""
    superuser_identity = running_app.superuser_identity

    # 1. Draft record is valid.
    with does_not_raise():
        RecordStatusConstraint.check(superuser_identity, draft_record)

    # 2. Published record must have the ``Related`` relationship.
    with does_not_raise():
        RecordStatusConstraint.check(
            superuser_identity, published_record, PackageRelationship.RELATED.value
        )

    pytest.raises(
        InvalidPackageResourceError,
        RecordStatusConstraint.check,
        identity=superuser_identity,
        record=published_record,
        relationship_type=PackageRelationship.MANAGED.value,
    )

    # 3. Published record must be ``public`` to be linked using the ``Related`` relationship.
    access = published_record.access.dump()

    # 3.1. Valid case
    published_record.access.protection.set(record="public")

    with does_not_raise():
        RecordStatusConstraint.check(
            superuser_identity, published_record, PackageRelationship.RELATED.value
        )

    # 3.2. Invalid case
    published_record.access.protection.set(record="restricted")

    pytest.raises(
        InvalidPackageResourceError,
        RecordStatusConstraint.check,
        identity=superuser_identity,
        record=published_record,
        relationship_type=PackageRelationship.RELATED.value,
    )


def test_package_relationship_constraint(
    db, running_app, anyuser_identity, draft_record, published_record, minimal_record
):
    """Test the Package Relationship constraint."""
    superuser_identity = running_app.superuser_identity

    # 1. Resources not linked to a package is valid.
    with does_not_raise():
        PackageRelationshipConstraint.check(
            superuser_identity, draft_record, PackageRelationship.RELATED.value
        )

        PackageRelationshipConstraint.check(
            superuser_identity, published_record, PackageRelationship.RELATED.value
        )

    # 2. Resources linked to a package must have the relationship ``Related``

    # 2.1. Valid case
    package = GEOPackageDraft.create(minimal_record)
    package.commit()
    db.session.commit()

    published_record.parent.relationship.managed_by = package
    published_record.parent.commit()

    with does_not_raise():
        PackageRelationshipConstraint.check(
            superuser_identity,
            published_record,
            PackageRelationship.RELATED.value,
            package=package,
        )

    # 2.2. Invalid case
    package2 = GEOPackageDraft.create(minimal_record)
    package2.commit()
    db.session.commit()

    pytest.raises(
        InvalidPackageResourceError,
        PackageRelationshipConstraint.check,
        identity=superuser_identity,
        record=published_record,
        relationship_type=PackageRelationship.MANAGED.value,
        package=package2,
    )


def test_published_package_constraint(
    db, running_app, draft_record, published_record, minimal_record
):
    """Test the Published Package constraint."""
    superuser_identity = running_app.superuser_identity

    # 1. Not published package is valid.
    with does_not_raise():
        PublishedPackageConstraint.check(
            identity=superuser_identity,
            relationship_type=PackageRelationship.RELATED.value,
            package=draft_record,
        )

    # 2. Published packaged must have the relationship ``Related``

    # 2.1. Valid case
    with does_not_raise():
        PublishedPackageConstraint.check(
            identity=superuser_identity,
            relationship_type=PackageRelationship.RELATED.value,
            package=published_record,
        )

    # 2.2. Invalid case
    pytest.raises(
        InvalidRelationshipError,
        PublishedPackageConstraint.check,
        identity=superuser_identity,
        relationship_type=PackageRelationship.MANAGED.value,
        package=published_record,
    )
