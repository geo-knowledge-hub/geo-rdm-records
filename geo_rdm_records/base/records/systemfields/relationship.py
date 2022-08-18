# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Records API."""

from invenio_records.systemfields import SystemField


class BaseRelationshipField(SystemField):
    """System field for managing record relationship."""

    def __init__(self, key, relationship_obj_cls):
        """Initializer."""
        self._relationship_obj_cls = relationship_obj_cls
        super().__init__(key=key)

    def obj(self, instance):
        """Get the record relationship object."""
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
            self.set_dictkey(record, obj.dump(), create_if_missing=True)
