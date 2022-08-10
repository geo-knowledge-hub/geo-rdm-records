# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resource type for the Related Records SystemField."""

from sqlalchemy.orm.exc import NoResultFound

from geo_rdm_records.records.api import GEODraft, GEORecord


class RecordProxy:
    """Class to proxy record access from the database."""

    record_cls = GEORecord
    """Record API class."""

    draft_cls = GEODraft
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

        self.record_cls = record_cls or RecordProxy.record_cls
        self.draft_cls = draft_cls or RecordProxy.draft_cls

        if isinstance(record, self.record_cls):
            self._entity = record
            self.record_id = record.pid.pid_value

        elif isinstance(record, str):  # record id (e.g., '0pfec-m8509')
            self.record_id = record

        elif isinstance(
            record, dict
        ):  # record id into a dict (e.g., { 'id': '0pfec-m8509' })
            self.record_id = record["id"]

        else:
            raise TypeError("Invalid record definition.")

    def dump(self):
        """Dump the record as a dictionary."""
        return {"id": self.record_id}

    def resolve(self):
        """Resolve the record entity (e.g., RDMRecord) via a database query."""
        if self._entity is None:

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

    def __hash__(self):
        """Return hash(self)."""
        return self.record_id

    def __eq__(self, other):
        """Return self == other."""
        return self.record_id == other

    def __ne__(self, other):
        """Return self != other."""
        return not self == other

    def __str__(self):
        """Return str(self)."""
        return str(self.resolve())

    def __repr__(self):
        """Return repr(self)."""
        return repr(self.resolve())


class RecordsProxy(list):
    """A list of records."""

    record_proxy_cls = RecordProxy
    """Class used to proxy the records from the database."""

    def __init__(self, records=None, record_proxy_cls=None):
        """Initializer."""
        self.record_proxy_cls = record_proxy_cls or RecordsProxy.record_proxy_cls

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
        super().remove(record)

    def dump(self):
        """Dump the records."""
        return [record.dump() for record in self]
