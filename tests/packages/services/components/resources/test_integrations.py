# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Access component for Package resources."""

from copy import copy

from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    PackageRelationship,
)
from geo_rdm_records.modules.packages.services.components.resources import (
    PackageResourceAccessComponent,
    PackageResourceCommunityComponent,
)
from geo_rdm_records.modules.rdm.records.api import GEODraft


def test_package_resource_access_component(running_app, minimal_record, es_clear):
    """Test the ``access`` component for package resources."""
    # 1. Creating a restricted package (`record` and `files`)
    package_access = dict(record="restricted", files="restricted")

    package_metadata = copy(minimal_record)
    package_metadata.update({"access": package_access})

    package_draft = GEOPackageDraft.create(package_metadata)
    package_draft.commit()

    # 2. Creating a public resource (`record` and `files`)
    resource_draft = GEODraft.create(minimal_record)
    resource_draft.commit()

    # 3. Validating that the access objects are different
    assert package_draft.access != resource_draft.access

    # 4. Using the component to transfer the access from the ``package`` to the ``resource``
    component = PackageResourceAccessComponent(None)

    component.package_add_resource(
        None, package_draft, resource_draft, PackageRelationship.MANAGED.value
    )

    assert resource_draft.access == package_draft.access


def test_package_resource_community_component(
    running_app, minimal_record, community_record, es_clear
):
    """Test the ``community`` component for package resources."""
    # 1. Creating a package
    package_metadata = copy(minimal_record)

    package_draft = GEOPackageDraft.create(package_metadata)
    package_draft.commit()

    # 2. Associating the package with a community.
    package_draft.parent.communities.add(community_record)

    # 3. Creating a package resource
    resource_draft = GEODraft.create(minimal_record)
    resource_draft.commit()

    # 4. Validating that the access objects are different
    assert package_draft.parent.communities.ids != resource_draft.parent.communities.ids

    # 5. Associating the package and the resource
    resource_draft.parent.relationship.managed_by = package_draft.parent
    resource_draft.parent.commit()
    resource_draft.commit()

    # 6. Using the component to ``tag`` the resource with
    #    the communities from the package.
    component = PackageResourceCommunityComponent(None)
    component.package_add_resource(
        None, package_draft, resource_draft, PackageRelationship.MANAGED.value
    )

    assert package_draft.parent.communities.ids == resource_draft.parent.communities.ids
