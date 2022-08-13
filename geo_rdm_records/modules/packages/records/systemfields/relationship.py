# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Package Relationship System Field."""

from geo_rdm_records.base.records.systemfields.proxy import (
    BaseRecordProxy,
    BaseRecordsProxy,
)
from geo_rdm_records.base.records.systemfields.relationship import BaseRelationshipField


class RecordProxy(BaseRecordProxy):
    """Class to proxy record access from the database."""

    record_cls = "GEORecord"
    """Record API class."""

    draft_cls = "GEODraft"
    """Draft Record API class."""


class RecordsProxy(BaseRecordsProxy):
    """A list of records."""

    record_proxy_cls = RecordProxy
    """Class used to proxy the records from the database."""


class PackageRelationship:
    """Related record management for specific versions of a record."""

    linked_resources_cls = RecordsProxy
    """List class used to handle the records."""

    def __init__(
        self, managed_resources=None, related_resources=None, linked_resources_cls=None
    ):
        """Create a new related record object for a record."""
        linked_resources_cls = (
            linked_resources_cls or PackageRelationship.linked_resources_cls
        )

        # In the GEO Knowledge Hub, the relation is always
        # between packages and resources. So, if not specified,
        # we define empty values using the same class for both
        # ``related`` and ``managed`` resources.
        self.related_resources = (
            related_resources if related_resources else linked_resources_cls()
        )
        self.managed_resources = (
            managed_resources if managed_resources else linked_resources_cls()
        )

        self.errors = []

    @property
    def managed(self):
        """An alias for the ``managed_resources`` property."""
        return self.managed_resources

    @property
    def related(self):
        """An alias for the ``related_resources`` property."""
        return self.related_resources

    def dump(self):
        """Dump the field values as dictionary."""
        relationship = {
            "managed_resources": self.managed_resources.dump(),
            "related_resources": self.related_resources.dump(),
        }

        return relationship

    def refresh_from_dict(self, relationship_dict):
        """Re-initialize the ``Relationship`` object using the given dictionary."""
        new_relationship_obj = self.from_dict(relationship_dict)

        self.errors = new_relationship_obj.errors
        self.managed_resources = new_relationship_obj.managed_resources
        self.related_resources = new_relationship_obj.related_resources

    @classmethod
    def from_dict(cls, relationship_dict, linked_resources_cls=None):
        """Create a new Relationship object from the specified ``relationship`` object."""
        linked_resources_cls = linked_resources_cls or cls.linked_resources_cls
        errors = []

        # defining the default values
        related_resources = linked_resources_cls()
        managed_resources = linked_resources_cls()

        if relationship_dict:
            # Related resources
            for related_resource in relationship_dict.get("related_resources", []):
                try:
                    related_resources.add(related_resource)
                except Exception as e:
                    errors.append(e)

            # Managed resources
            for managed_resource in relationship_dict.get("managed_resources", []):
                try:
                    managed_resources.add(managed_resource)
                except Exception as e:
                    errors.append(e)

        relationship = cls(
            managed_resources=managed_resources, related_resources=related_resources
        )
        relationship.errors = errors

        return relationship

    def __repr__(self):
        """Return repr(self)."""
        return ("<{} (managed_resources: {}, related_resources: {})>").format(
            type(self).__name__,
            len(self.managed_resources or []),
            len(self.related_resources or []),
        )


class PackageRelationshipField(BaseRelationshipField):
    """System field for managing record relationship."""

    def __init__(self, key="relationship", relationship_obj_cls=PackageRelationship):
        """Initializer."""
        super().__init__(key=key, relationship_obj_cls=relationship_obj_cls)
