# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Relationship."""

from invenio_records.api import Record

from geo_rdm_records.base.records.systemfields import (
    BaseRecordProxy,
    BaseRelationshipField,
)


class RecordProxy(BaseRecordProxy):
    """Class to proxy record access from the database."""

    record_cls = "GEOPackageRecord"
    """Record API class."""

    draft_cls = "GEOPackageDraft"
    """Draft Record API class."""


class RecordRelationship:
    """Related record management for specific versions of a package."""

    linked_resource_cls = RecordProxy
    """Class used to handle the package records."""

    def __init__(self, managed_by=None, linked_resource_cls=None):
        """Create a new related record object for a record."""
        linked_resource_cls = (
            linked_resource_cls or RecordRelationship.linked_resource_cls
        )

        self.errors = []
        self._record_manager = (
            linked_resource_cls(managed_by)
            if type(managed_by) != linked_resource_cls
            else managed_by
        )

    #
    # Properties
    #
    @property
    def managed_by(self):
        """Return the manager of the record."""
        return self._record_manager.resolve() if self._record_manager else {}

    @managed_by.setter
    def managed_by(self, obj):
        """Define new value as the manager of the record."""
        self.refresh(obj)

    @managed_by.deleter
    def managed_by(self):
        """Delete the record manager."""
        self._record_manager = {}

    #
    # Auxiliary methods
    #
    def refresh(self, relationship_dict):
        """Re-initialize the ``Relationship`` object using the given dictionary."""
        new_relationship_obj = self.from_dict(relationship_dict)

        self.errors = new_relationship_obj.errors
        self._record_manager = new_relationship_obj._record_manager

    #
    # Data handling interface
    #
    @classmethod
    def from_dict(cls, relationship_dict, linked_resource_cls=None):
        """Create a new Relationship object from the specified ``relationship`` object."""
        linked_resource_cls = linked_resource_cls or cls.linked_resource_cls
        errors = []

        # defining the default values
        managed_by = None

        if relationship_dict:
            try:
                if "managed_by" in relationship_dict:
                    relationship_dict = relationship_dict.get("managed_by")

                managed_by = linked_resource_cls(relationship_dict)
            except Exception as e:
                errors.append(e)

        relationship = cls(managed_by=managed_by)
        relationship.errors = errors

        return relationship

    def dump(self):
        """Dump the field values as dictionary."""
        if self._record_manager:
            return dict(managed_by=self._record_manager.dump())

        return {}

    #
    # Dunder methods
    #
    def __repr__(self):
        """Return repr(self)."""
        return ("<{} (is_managed: {})>").format(
            type(self).__name__, self._record_manager is None
        )


class RecordRelationshipField(BaseRelationshipField):
    """System field for managing record relationship."""

    def __init__(self, key="relationship", relationship_obj_cls=RecordRelationship):
        """Initializer."""
        super().__init__(key=key, relationship_obj_cls=relationship_obj_cls)

    def set_obj(self, record, obj):
        """Set the relationship object."""
        if isinstance(obj, dict):
            obj = self._relationship_obj_cls.from_dict(obj)
        elif isinstance(obj, Record):
            obj = self._relationship_obj_cls(obj)

        assert isinstance(obj, self._relationship_obj_cls)

        self._set_cache(record, obj)
