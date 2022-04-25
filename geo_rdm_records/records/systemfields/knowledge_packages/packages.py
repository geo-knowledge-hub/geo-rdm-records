# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from invenio_pidstore.errors import PIDUnregistered

# ToDo: Review if the use of this class is required.
from invenio_records.api import Record


class KnowledgePackage:
    """An abstraction between Knowledge Package entities (Record) and specifications as dict.

    Note:
        This class is based on Owner abstraction from Invenio-RDM-Records.

    See:
        https://github.com/inveniosoftware/invenio-rdm-records/blob/4bddf95d3ca0b784c45746a5d2280c10824c9ca4/invenio_rdm_records/records/systemfields/access/owners.py#L14
    """

    def __init__(self, knowledge_package):
        """Initializer."""
        self._entity = None
        self.package_id = None

        if isinstance(knowledge_package, str):
            self.package_id = knowledge_package

        elif isinstance(knowledge_package, Record):  # (GEODraft, GEORecord)):
            self._entity = knowledge_package
            self.package_id = knowledge_package.json["id"]

        else:
            raise TypeError(
                "Invalid Knowledge Package type: {}".format(type(knowledge_package))
            )

    def dump(self):
        """Dump the Knowledge Package as a plain object."""
        return self.package_id

    def resolve(self):
        """Resolve the owner entity (e.g., User) via a database query (PID Resolver for the record case)."""
        # ToDo: check if this import is required here.
        from geo_rdm_records.records.api import GEODraft, GEORecord

        try:
            self._entity = GEODraft.pid.resolve(self.package_id, registered_only=False)
        except PIDUnregistered:
            self._entity = GEORecord.pid.resolve(self.package_id)

        return self._entity

    def __hash__(self):
        """Return hash(self)"""
        return hash(self.package_id)

    def __eq__(self, __o):
        """Return self == other."""
        if type(self) != type(__o):
            return False

        return self.package_id == __o.package_id

    def __ne__(self, __o):
        """Return self != other."""
        return not self == __o

    def __str__(self):
        """Return str(self)."""
        return str(self.resolve())

    def __repr__(self):
        """Return repr(self)."""
        return repr(self.resolve())


class KnowledgePackages(list):
    """A list of Knowledge Packages associated to a record.

    Note:
        This class is based on Owner list (Owners) abstraction from Invenio-RDM-Records.

    See:
        https://github.com/inveniosoftware/invenio-rdm-records/blob/4bddf95d3ca0b784c45746a5d2280c10824c9ca4/invenio_rdm_records/records/systemfields/access/owners.py#L88
    """

    knowledge_package_cls = KnowledgePackage

    def __init__(self, knowledge_packages=None, knowledge_package_cls=None):
        """Initializer."""
        self.knowledge_package_cls = (
            knowledge_package_cls or KnowledgePackages.knowledge_package_cls
        )

        for knowledge_package in knowledge_packages or []:
            self.add(knowledge_package)

    def add(self, knowledge_package):
        """Add the specified Knowledge Package to the list of Knowledge Packages."""
        self.append(knowledge_package)

    def append(self, knowledge_package):
        """Add the specified Knowledge Package to the list of Knowledge Packages.

        Args:
            knowledge_package (invenio_records.Record): The Knowledge Package associated with the record.
        """
        if not isinstance(knowledge_package, self.knowledge_package_cls):
            knowledge_package = self.knowledge_package_cls(knowledge_package)

        if knowledge_package not in self:
            super().append(knowledge_package)

    def extend(self, knowledge_packages):
        """Add all new items from the specified Knowledge Package to this list."""
        for knowledge_package in knowledge_packages:
            self.add(knowledge_package)

    def remove(self, knowledge_package):
        """Remove the specified Knowledge Package from the list of Knowledge Packages"""
        if not isinstance(knowledge_package, self.knowledge_package_cls):
            knowledge_package = self.knowledge_package_cls(knowledge_package)

        super().remove(knowledge_package)

    def dump(self):
        """Dump the Knowledge Packages as a list of string (Knowledge Package ID)."""
        return [knowledge_package.dump() for knowledge_package in self]
