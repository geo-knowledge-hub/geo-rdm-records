# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Package Related Records system field."""

from invenio_records.dictutils import dict_lookup, parse_lookup_key
from invenio_records.systemfields import SystemField


class AttrProxy:
    """Attribute proxy.

    Note:
        This class was implemented based on ``AttrProxy`` from Invenio Requests.

    Note:
        (From Invenio Requests) The main purpose of this proxy, is to use data
        stored on the current record if available, instead of quering the database
        for the related record.
    """

    def __init__(self, record_cls, record, data):
        """Initialize the attribute proxy."""
        self._data = data
        self._id = record.id if record else data["id"]
        self._record = record
        self._record_cls = record_cls

    def get_object(self):
        """Get the underlying record."""
        if self._record is None:
            self._record = self._record_cls.get_record(self._id)
        return self._record

    def __getattr__(self, attr):
        """Attribute access."""
        if self._record is None:
            if attr in self._data:
                return self._data[attr]
            self._record = self._record_cls.get_record(self._id)
        return getattr(self._record, attr)

    def __getitem__(self, attr):
        """Item access."""
        if self._record is None:
            if attr in self._data:
                return self._data[attr]
            self._record = self._record_cls.get_record(self._id)
        return self._record[attr]


class RelatedRecordsField(SystemField):
    """Related records field.

    Note:
        This class was implemented based on ``RelatedRecord`` from Invenio Requests.
    """

    def __init__(self, record_cls, *args, keys=None, attrs=None, **kwargs):
        """Field initializer."""
        self._record_cls = record_cls
        # Dump just 'id' by default.
        self._dump_keys = keys or []
        self._dump_attrs = attrs or []
        super().__init__(*args, **kwargs)

    #
    # Life-cycle hooks
    #
    def _dump(self, proxy):
        """Dump given attributes from a proxy.

        Note, only top-level keys are supported.
        """
        data = {"id": str(proxy.id)}
        for k in self._dump_attrs:
            data[k] = getattr(proxy, k)
        for k in self._dump_keys:
            data[k] = proxy[k]

        # Add a version counter "@v" used for optimistic
        # concurrency control. It allows to search for all
        # outdated records and reindex them.
        data["@v"] = f"{proxy.id}::{proxy.revision_id}"
        return data

    def pre_commit(self, record):
        """Called before a record is committed."""
        proxy = getattr(record, self.attr_name)
        if proxy is not None:
            self.set_dictkey(record, self._dump(proxy), create_if_missing=True)

    #
    # Helpers
    #
    def _mutate_to_proxy(self, records_or_ids):
        records_or_ids_mutated = []
        for record_or_id in records_or_ids:

            if isinstance(record_or_id, str):
                proxy = AttrProxy(self._record_cls, None, {"id": record_or_id})
            elif isinstance(record_or_id, self._record_cls):
                proxy = AttrProxy(self._record_cls, record_or_id, None)
            elif isinstance(record_or_id, AttrProxy):
                proxy = record_or_id
            else:
                raise ValueError("Defined value can't be used as a related record.")

            records_or_ids_mutated.append(proxy)

        return records_or_ids_mutated

    def _unset_cache(self, record):
        """Unset an object on the instance's cache."""
        if hasattr(record, "_obj_cache"):
            record._obj_cache.pop(self.attr_name, None)

    def del_value(self, record):
        """Delete the record relation."""
        # Unset cache if None.
        self._unset_cache(record)
        try:
            keys = parse_lookup_key(self.key)
            parent = dict_lookup(record, keys, parent=True)
            parent.pop(keys[-1], None)
        except KeyError:
            pass
        return

    def set_value(self, record, records_or_ids):
        """Set the record (by id, record or proxy)."""
        # Unset cache if None.
        if records_or_ids is None:
            self.del_value(record)
            return

        mutated_records_or_ids = self._mutate_to_proxy(records_or_ids)

        self._set_cache(record, mutated_records_or_ids)

    def get_value(self, record):
        """Get the data."""
        proxy = self._get_cache(record)
        if proxy is not None:
            return proxy

        data = self.get_dictkey(record)
        if data is not None:
            # ToDo: To be verified.
            proxy = AttrProxy(self._record_cls, None, data)
            self._set_cache(record, proxy)
        else:
            proxy = None

        return proxy
