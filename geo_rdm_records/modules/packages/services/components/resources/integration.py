# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources component."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records.dictutils import dict_lookup

from geo_rdm_records.base.services.components.constraints import ConstrainedComponent
from geo_rdm_records.modules.packages.errors import InvalidRelationshipError
from geo_rdm_records.modules.packages.records.api import PackageRelationship

from .constraints import (
    CommunityRelationshipConstraint,
    PackageRelationshipConstraint,
    PublishedPackageConstraint,
    ValidDraftConstraint,
)


class PackageResourceIntegrationComponent(ConstrainedComponent):
    """Constrained component to validate and integrate packages and resources."""

    constraints = [
        CommunityRelationshipConstraint,
        # ValidDraftConstraint,
        PackageRelationshipConstraint,
        PublishedPackageConstraint,
    ]

    #
    # Package/resource handling methods
    #
    def package_add_resource(
        self,
        identity,
        package=None,
        resource=None,
        relationship_type=None,
        validate=True,
        errors=None,
        **kwargs
    ):
        """Add resource to a package."""
        if validate:
            try:
                self.validate(
                    identity=identity,
                    resource=resource,
                    package=package,
                    relationship_type=relationship_type,
                    service=current_rdm_records_service,
                )
            except InvalidRelationshipError:
                errors.append(
                    dict(
                        record=resource.pid.pid_value,
                        message="This resource can't be associated with the package.",
                    )
                )

        # now, it is possible to link the package/resource
        package.relationship.resources.append(resource)
        resource.relationship.packages.append(package)

    def package_delete_resource(
        self,
        identity,
        package=None,
        resource=None,
        relationship_type=None,
        validate=True,
        errors=None,
        **kwargs
    ):
        """Remove resource from a package."""
        if validate:
            try:
                self.validate(
                    identity=identity,
                    resource=resource,
                    package=package,
                    relationship_type=relationship_type,
                    service=current_rdm_records_service,
                )
            except InvalidRelationshipError:
                errors.append(
                    dict(
                        record=resource.pid.pid_value,
                        message="This resource can't be removed from the package.",
                    )
                )

        package_resources = list(
            map(lambda x: x["id"], dict_lookup(package, "relationship.resources"))
        )
        resource_packages = list(
            map(lambda x: x["id"], dict_lookup(resource, "relationship.packages"))
        )

        if resource.pid.pid_value in package_resources:
            package.relationship.resources.remove(resource)

        if package.pid.pid_value in resource_packages:
            resource.relationship.packages.remove(package)


class PackageResourceCommunityComponent(ServiceComponent):
    """Component to validate and integrate packages and resources communities."""

    def package_add_resource(
        self, identity, package=None, resource=None, relationship_type=None, **kwargs
    ):
        """Add resource to a package."""
        if (
            relationship_type == PackageRelationship.MANAGED.value
            and package.parent == resource.parent.relationship.managed_by
        ):
            if package.parent.communities:
                # ToDo: Probably, we need to review and improve this. What we are
                #       doing is 'hard copy' the communities definition from the
                #       package to the resource to enable the search capabilities
                #       for both packages and resources inside a community.
                #       We are not using the ``add`` method because at this moment,
                #       we not need use the database table with the requests.
                resource.parent.communities.from_dict(
                    package.parent.communities.to_dict()
                )
