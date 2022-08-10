# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Package Relationship System Field."""

from invenio_records.systemfields import SystemField

from .record_proxy import RecordsProxy


class Relationship:
    """Related record management for specific versions of a record."""

    linked_resources_cls = RecordsProxy
    """List class used to handle the records."""

    def __init__(
        self, managed_resources=None, related_resources=None, linked_resources_cls=None
    ):
        """Create a new related record object for a record."""
        linked_resources_cls = linked_resources_cls or Relationship.linked_resources_cls

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
            "managed_resources": self.related_resources.dump(),
            "related_resources": self.managed_resources.dump(),
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
                    related_resources.add(
                        related_resources.record_proxy_cls(related_resource)
                    )
                except Exception as e:
                    errors.append(e)

            # Managed resources
            for managed_resource in relationship_dict.get("managed_resources", []):
                try:
                    managed_resources.add(
                        managed_resources.record_proxy_cls(managed_resource)
                    )
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


class RelationshipField(SystemField):
    """System field for managing record relationship."""

    def __init__(self, key="relationship", relationship_obj_cls=Relationship):
        """Initializer."""
        self._relationship_obj_cls = relationship_obj_cls
        super().__init__(key=key)

    def obj(self, instance):
        """Get the relationship object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        data = self.get_dictkey(instance)
        if data:
            obj = self._relationship_obj_cls.from_dict(data)
        else:
            obj = self._relationship_obj_cls()

        self._set_cache(instance, obj)
        return obj

    def set_obj(self, record, obj):
        """Set the relationship object."""
        # We accept both dicts and relationship class objects.
        if isinstance(obj, dict):
            obj = self._relationship_obj_cls.from_dict(obj)

        assert isinstance(obj, self._relationship_obj_cls)

        # We do not dump the object until the pre_commit hook
        # I.e. record.relationship != record['relationship']
        self._set_cache(record, obj)

    def __get__(self, record, owner=None):
        """Get the record relationship object."""
        if record is None:
            # access by class
            return self

        # access by object
        return self.obj(record)

    def __set__(self, record, obj):
        """Set the records relationship object."""
        self.set_obj(record, obj)

    def pre_commit(self, record):
        """Dump the configured values before the record is committed."""
        obj = self.obj(record)
        if obj is not None:
            record[self.key] = obj.dump()
