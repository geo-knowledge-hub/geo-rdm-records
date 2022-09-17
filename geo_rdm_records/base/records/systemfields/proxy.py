# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record proxy for system fields."""

from sqlalchemy.orm.exc import NoResultFound

from geo_rdm_records.class_factory import ClassFactory


class BaseRecordProxy:
    """Class to proxy record access from the database."""

    record_cls = None
    """Record API class."""

    draft_cls = None
    """Draft Record API class."""

    def __init__(self, record, record_cls=None, draft_cls=None, allow_drafts=True):
        """Initializer.

        Args:
            record (Union[str, dict, invenio_records.Record]): Record definition.

            record_cls (invenio_records.Record): Record class to handle record from the database.

            draft_cls (invenio_records.Record): Record class to handle draft record from the database.

            allow_drafts (bool): Flag to set if draft can be handled by the proxy.
        """
        self._entity = None  # record cache

        self.record_id = None
        self.allow_drafts = allow_drafts

        # we are using the instance bellow to get the ``record_cls`` and
        # the ``draft_cls`` to allow subclassing.
        self.draft_cls = draft_cls or self.draft_cls
        self.record_cls = record_cls or self.record_cls

        # updating the classes
        self.record_cls = self._use_factory(self.record_cls)
        self.draft_cls = self._use_factory(self.draft_cls)

        # storing the record in the class instance
        self._store_record(record)

    #
    # Auxiliary methods
    #
    def _store_record(self, record):
        """Store the record values in the class."""
        if isinstance(record, (self.record_cls, self.draft_cls)):
            self._entity = record
            self.record_id = record.pid.pid_value

        elif isinstance(record, str):  # record id (e.g., '0pfec-m8509')
            self.record_id = record

        elif isinstance(
            record, dict
        ):  # record id into a dict (e.g., { 'id': '0pfec-m8509' })
            self.record_id = record["id"]

        elif isinstance(record, BaseRecordProxy):
            self.record_id = record.record_id

    def _use_factory(self, value):
        """Load defined classes from the ``ClassFactory``."""
        return ClassFactory.resolve(value) if type(value) == str else value

    #
    # Data handling interface
    #
    def resolve(self):
        """Resolve the record entity (e.g., RDMRecord)."""
        if self._entity is None and self.record_id is not None:
            try:
                self._entity = self.record_cls.pid.resolve(
                    self.record_id, registered_only=False
                )
            except NoResultFound:
                if self.allow_drafts:
                    self._entity = self.draft_cls.pid.resolve(
                        self.record_id, registered_only=False
                    )

        return self._entity

    def dump(self):
        """Dump the record as a dictionary."""
        res = {}

        if self.record_id:
            res = {"id": self.record_id}

        return res

    #
    # Dunder methods
    #
    def __hash__(self):
        """Return hash(self)."""
        return self.record_id

    def __eq__(self, other):
        """Return self == other."""
        return self.record_id == other.record_id

    def __ne__(self, other):
        """Return self != other."""
        return not self == other

    def __str__(self):
        """Return str(self)."""
        return str(self.resolve())

    def __repr__(self):
        """Return repr(self)."""
        return repr(self.resolve())


class BaseRecordsProxy(list):
    """A list of records."""

    record_proxy_cls = BaseRecordProxy
    """Class used to proxy the records from the database."""

    def __init__(self, records=None, record_proxy_cls=None):
        """Initializer."""
        self.record_proxy_cls = record_proxy_cls or self.record_proxy_cls

        for record in records or []:
            self.add(record)

    def add(self, record):
        """Alias for self.append(record)."""
        self.append(record)

    def append(self, record):
        """Add a new record to the list of records."""
        record_proxy = self.record_proxy_cls(record)

        if record_proxy not in self:
            super().append(record_proxy)

    def extend(self, records):
        """Add all new items from another list to the current list."""
        for record in records:
            self.add(record)

    def remove(self, record):
        """Remove the specified record from the list of records."""
        record_proxy = record

        if type(record) != self.record_proxy_cls:
            record_proxy = self.record_proxy_cls(record)

        super().remove(record_proxy)

    def dump(self):
        """Dump the records."""
        return [record.dump() for record in self]
