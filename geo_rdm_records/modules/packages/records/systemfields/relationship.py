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

    resources_cls = RecordsProxy
    """List class used to handle the records."""

    def __init__(self, resources=None, resources_cls=None):
        """Create a new related record object for a record."""
        resources_cls = resources_cls or PackageRelationship.resources_cls

        # In the GEO Knowledge Hub, the relation is always
        # between packages and resources.
        self._resources = resources if resources else resources_cls()

        self.errors = []

    @property
    def resources(self):
        """An alias for the ``resources`` property."""
        return self._resources

    def dump(self):
        """Dump the field values as dictionary."""
        relationship = {
            "resources": self.resources.dump(),
        }

        return relationship

    def refresh_from_dict(self, relationship_dict):
        """Re-initialize the ``Relationship`` object using the given dictionary."""
        new_relationship_obj = self.from_dict(relationship_dict)

        self.errors = new_relationship_obj.errors
        self._resources = new_relationship_obj.resources

    @classmethod
    def from_dict(cls, relationship_dict, resources_cls=None):
        """Create a new Relationship object from the specified ``relationship`` object."""
        resources_cls = resources_cls or cls.resources_cls
        errors = []

        # defining the default values
        resources = resources_cls()

        if relationship_dict:
            # Resources
            for resource in relationship_dict.get("resources", []):
                try:
                    resources.add(resource)
                except Exception as e:
                    errors.append(e)

        relationship = cls(
            resources=resources,
        )
        relationship.errors = errors

        return relationship

    def __repr__(self):
        """Return repr(self)."""
        return "<{} (resources: {})>".format(
            type(self).__name__,
            len(self.resources or []),
        )


class PackageRelationshipField(BaseRelationshipField):
    """System field for managing record relationship."""

    def __init__(self, key="relationship", relationship_obj_cls=PackageRelationship):
        """Initializer."""
        super().__init__(key=key, relationship_obj_cls=relationship_obj_cls)
