# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources component."""

from invenio_rdm_records.proxies import current_rdm_records_service

from geo_rdm_records.base.services.components.constraints import ConstrainedComponent
from geo_rdm_records.modules.packages.records.api import PackageRelationship

from .constraints import (
    CommunityRelationshipConstraint,
    PackageRelationshipConstraint,
    PublishedPackageConstraint,
    RecordStatusConstraint,
    ValidDraftConstraint,
)


class PackageResourceIntegrationComponent(ConstrainedComponent):
    """Constrained component to validate and integrate packages and resources."""

    constraints = [
        CommunityRelationshipConstraint,
        ValidDraftConstraint,
        RecordStatusConstraint,
        PackageRelationshipConstraint,
        PublishedPackageConstraint,
    ]

    #
    # Package/resource handling methods
    #
    def add_package_resource(
        self, identity, record=None, resource=None, relationship_type=None, **kwargs
    ):
        """Add resource to a package."""
        self.validate(
            identity=identity,
            record=resource,
            package=record,
            relationship_type=relationship_type,
            service=current_rdm_records_service,
        )

        # now, it is possible to link the package/resource
        if relationship_type == PackageRelationship.MANAGED.value:
            # bidirectional relation

            # 1. from package to resource
            record.relationship.managed_resources.append(resource)

            # 2. from resource to package
            resource.parent.relationship.managed_by = record

        elif relationship_type == PackageRelationship.RELATED.value:
            # unidirectional relation

            # 1. from package to resource
            record.relationship.related_resources.append(resource)

    def delete_package_resource(
        self, identity, record=None, resource=None, relationship_type=None, **kwargs
    ):
        """Remove resource from a package."""
        self.validate(
            identity=identity,
            record=resource,
            package=record,
            relationship_type=relationship_type,
            service=current_rdm_records_service,
        )

        if relationship_type == PackageRelationship.MANAGED.value:
            # bidirectional relation

            # 1. remove from package
            record.relationship.managed_resources.remove(resource)

            # 2. remove from resource
            del resource.relationship.managed_by

        elif resource == PackageRelationship.RELATED.value:
            # unidirectional relation

            # 1. remove from package
            record.relationship.related_resources.remove(resource)
