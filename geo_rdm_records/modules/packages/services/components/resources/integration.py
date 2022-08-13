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
    def package_add_resource(
        self,
        identity,
        record=None,
        resource=None,
        relationship_type=None,
        validate=True,
        **kwargs
    ):
        """Add resource to a package."""
        if validate:
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

    def package_delete_resource(
        self,
        identity,
        record=None,
        resource=None,
        relationship_type=None,
        validate=True,
        **kwargs
    ):
        """Remove resource from a package."""
        if validate:
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
            del resource.parent.relationship.managed_by

        elif relationship_type == PackageRelationship.RELATED.value:
            # unidirectional relation

            # 1. remove from package
            record.relationship.related_resources.remove(resource)

    def package_update_resource(
        self,
        identity,
        record=None,
        resource=None,
        relationship_type=None,
        validate=True,
        **kwargs
    ):
        """Update resource from a package."""
        if validate:
            self.validate(
                identity=identity,
                record=resource,
                package=record,
                relationship_type=relationship_type,
                service=current_rdm_records_service,
            )

        # checking for references of the given resource in both ``managed`` and ``related``
        # properties. We are not using the ``delete`` reference because in the update process
        # we are looking for a previous version of the ``resource`` not the current available
        # instance.
        try:
            record.relationship.managed_resources.remove(resource)
            del resource.parent.relationship.managed_by
        except (ValueError, AttributeError, IndexError):
            record.relationship.related_resources.remove(resource)

        self.package_add_resource(
            identity,
            record=record,
            resource=resource,
            relationship_type=relationship_type,
            validate=False,
            **kwargs
        )
