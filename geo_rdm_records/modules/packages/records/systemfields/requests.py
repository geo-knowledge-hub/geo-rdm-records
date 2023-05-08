# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Requests System Field."""

import collections

from invenio_records.dictutils import dict_lookup, parse_lookup_key
from invenio_records.systemfields import SystemField
from invenio_requests.records.systemfields.relatedrecord import AttrProxy


class AssistanceRequests(SystemField):
    """System field to manage assistance requests in packages."""

    def __init__(self, record_cls, *args, keys=None, attrs=None, **kwargs):
        """Initialize field."""
        self._record_cls = record_cls

        # Dump just 'id' by default
        self._dump_keys = keys or []
        self._dump_attrs = attrs or []

        super().__init__(*args, **kwargs)

    #
    # Properties
    #
    @property
    def _proxy_attrs(self):
        """Attributes to dump."""
        return set(self._dump_keys + self._dump_attrs)

    #
    # Auxiliary methods
    #
    def _dump(self, proxies):
        """Dump given attribute from a proxy."""
        proxies_data = []
        for proxy in proxies:
            data = dict(id=str(proxy.id))

            for k in self._dump_attrs:
                data[k] = getattr(proxy, k)

            for k in self._dump_keys:
                data[k] = proxy[k]

            # Add a version counter "@v" used for optimistic
            # concurrency control. It allows to search for all
            # outdated records and reindex them.
            data["@v"] = f"{proxy.id}::{proxy.revision_id}"

            proxies_data.append(data)

        return proxies_data

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

    def _prepare_value(self, record_or_id):
        """Set the record (by id, record, or proxy)."""
        # set value
        if isinstance(record_or_id, str):
            proxy = AttrProxy(
                self._record_cls, None, {"id": record_or_id}, attrs=self._proxy_attrs
            )

        elif isinstance(record_or_id, self._record_cls):
            proxy = AttrProxy(
                self._record_cls, record_or_id, None, attrs=self._proxy_attrs
            )

        elif isinstance(record_or_id, AttrProxy):
            proxy = record_or_id

        else:
            raise ValueError("Invalid value.")

        return proxy

        # self._set_cache(record, proxy)

    def set_values(self, record, associated_records):
        """Set `key` value in record."""
        proxies = []

        for associated_record in associated_records:
            try:
                associated_record_proxy = self._prepare_value(associated_record)

                proxies.append(associated_record_proxy)
            except ValueError:
                pass

        self._set_cache(record, proxies)

    def get_value(self, record):
        """Get `key` value from record."""
        proxies = self._get_cache(record)
        if proxies is not None:
            return proxies

        data = self.get_dictkey(record)

        if data is not None:  ## assuming that the stored data is a list of values
            proxies = []
            for row in data:
                row_proxy = AttrProxy(
                    self._record_cls, None, row, attrs=self._proxy_attrs
                )
                proxies.append(row_proxy)

            self._set_cache(record, proxies)
        else:
            proxies = None

        return proxies

    #
    # Life-cycle hooks
    #
    def pre_commit(self, record):
        """Called before a record is committed."""
        proxy = getattr(record, self.attr_name) or []

        if proxy is not None:
            self.set_dictkey(record, self._dump(proxy), create_if_missing=True)

    #
    # Data descriptor methods
    #
    def __get__(self, record, owner=None):
        """Get the persistent identifier."""
        if record is None:
            return self
        return self.get_value(record)

    def __set__(self, record, pids):
        """Set persistent identifier on record."""
        if not isinstance(pids, collections.Sequence):
            raise ValueError("Value must be a iterable element of records")

        self.set_values(record, pids)
