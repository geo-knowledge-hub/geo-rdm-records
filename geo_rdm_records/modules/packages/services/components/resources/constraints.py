# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources component constraints."""

from marshmallow.exceptions import ValidationError

from geo_rdm_records.base.services.components.constraints import BaseComponentConstraint
from geo_rdm_records.modules.packages.errors import (
    InvalidPackageResourceError,
    InvalidRelationshipError,
)
from geo_rdm_records.modules.packages.records.api import PackageRelationship


class CommunityRelationshipConstraint(BaseComponentConstraint):
    """Community relationship constraint.

    This constraint checks if a given record is linked
    to a community. The following rules are applied in this
    verification:

        1. Checks if the record is linked to a community. If not linked, then
        the given record is valid. But, if linked, the second rule is executed;

        2. Checks if the relationship type is equal to ``Related``. If not, the
        record cannot be used, and the constraint will fail.
    """

    @classmethod
    def check(
        cls,
        identity,
        resource=None,
        relationship_type=None,
        service=None,
        package=None,
        **kwargs
    ):
        """Check if the constraint is valid."""
        if (
            len(resource.parent.communities) != 0
            and relationship_type != PackageRelationship.RELATED.value
        ):
            raise InvalidPackageResourceError(resource)


class ValidDraftConstraint(BaseComponentConstraint):
    """Valid Draft constraint.

    This constraint checks if a given draft is valid and can be published.
    The following rules are applied in this verification:

        1. Checks if the record is ``Draft``. If it is not, the record is valid.
        But, if it is, the second rule is executed;

        2. Checks if the ``Draft`` is ready to be published (e.g., All required fields
        filled, files filled). If not ready, then the constraint fails;

        3. Checks if the current ``identity`` can perform the ``update_draft``
        action. We are not using any kind of ``system identity`` to avoid permissions leaks
        with incorrect users;

            Example:
                User 1 can access Record B, and User 2 can't access Record B. In this case, using a
                ``system identifier`` User 2 will be able to change the Record B via the Package.

        4. Checks if the relationship is equals to ``Managed``.
    """

    @classmethod
    def check(
        cls,
        identity,
        resource=None,
        relationship_type=None,
        service=None,
        package=None,
        **kwargs
    ):
        """Check if the constraint is valid."""
        if resource.is_draft:
            # checking if user has the permission to perform the ``update_draft`` action in the record.
            service.require_permission(identity, "update_draft", record=resource)

            # checking the relationship. ``Draft`` can only be associated in a ``Managed`` relationship.
            if relationship_type != PackageRelationship.MANAGED.value:
                raise InvalidRelationshipError(resource)

            # checking if the data is ready to be published
            record_item = service.result_item(service, identity, resource)

            # Validate the data - will raise ValidationError if not valid.
            try:
                service.schema.load(
                    data=record_item.data,
                    context=dict(identity=identity, pid=resource.pid, record=resource),
                    raise_errors=True,
                )
            except ValidationError as e:
                raise InvalidPackageResourceError(resource) from e


class PackageRelationshipConstraint(BaseComponentConstraint):
    """Package relationship constraint.

    This constraint checks if a given record is linked
    to a package. The following rules are applied in this
    verification:

        1. Checks if the record is linked to a package. If not linked, then
        the given record is valid. But, if linked, the second rule is executed;

        2. Checks if a record related to a package is using the relationship ``Related``.
        If not, the record cannot be used, and the constraint fails.
    """

    @classmethod
    def check(
        cls,
        identity,
        resource=None,
        relationship_type=None,
        service=None,
        package=None,
        **kwargs
    ):
        """Check if the constraint is valid."""
        managed_by = resource.parent.relationship.managed_by
        is_related_to_package = managed_by is not None and not (
            managed_by.pid.pid_value == package.parent.pid.pid_value
        )

        if (
            is_related_to_package
            and relationship_type != PackageRelationship.RELATED.value
        ):
            raise InvalidPackageResourceError(resource)


class PublishedPackageConstraint(BaseComponentConstraint):
    """Published package constraint.

    This constraint checks if a given package is published and if it is
    valid for modifications. The following rules are applied in this verification:

        1. Checks if the package is published. If it is not published, then
        the given package is valid. But, if published, the constraint fails.
    """

    @classmethod
    def check(
        cls,
        identity,
        resource=None,
        relationship_type=None,
        service=None,
        package=None,
        **kwargs
    ):
        """Check if the constraint is valid."""
        if package.is_published:
            raise InvalidRelationshipError(package)
