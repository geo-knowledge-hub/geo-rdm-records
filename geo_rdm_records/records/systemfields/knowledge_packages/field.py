# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from invenio_records.systemfields import SystemField

from geo_rdm_records.records.systemfields.knowledge_packages.packages import (
    KnowledgePackages,
)


class KnowledgePackageManager:
    """Knowledge Package manager for all versions of a record.

    Note:
        This class is based on RecordAccess from Invenio-RDM-Records.

    See: https://github.com/inveniosoftware/invenio-rdm-records/blob/4bddf95d3ca0b784c45746a5d2280c10824c9ca4/invenio_rdm_records/records/systemfields/access/field/record.py#L31
    """

    knowledge_packages_cls = KnowledgePackages

    def __init__(self, knowledge_packages=None, knowledge_packages_cls=None):
        """Create a new Knowledge Package Manager object for a record."""
        knowledge_packages_cls = (
            knowledge_packages_cls or KnowledgePackageManager.knowledge_packages_cls
        )

        self.errors = []
        self.knowledge_packages = (
            knowledge_packages if knowledge_packages else knowledge_packages_cls()
        )

    def dump(self):
        """Dump the field value as dictionary."""
        return self.knowledge_packages.dump()

    def refresh_from_dict(self, knowledge_packages_dict):
        """Re-initialize the Knowledge Packages object with the data in the knowledge_packages_dict."""
        new_knowledge_packages_obj = self.from_dict(knowledge_packages_dict)
        self.errors = new_knowledge_packages_obj.errors
        self.knowledge_packages = new_knowledge_packages_obj.knowledge_packages

    @classmethod
    def from_dict(cls, knowledge_packages_dict, knowledge_packages_cls=None):
        """Create a new Knowledge Package object from the specified 'knowledge packages' property."""
        errors = []
        knowledge_packages_cls = knowledge_packages_cls or cls.knowledge_packages_cls

        knowledge_packages = knowledge_packages_cls()

        if knowledge_packages_dict:
            for knowledge_package in knowledge_packages_dict:
                try:
                    knowledge_packages.add(
                        knowledge_packages.knowledge_package_cls(knowledge_package)
                    )
                except Exception as e:
                    errors.append(e)

        knowledge_packages = cls(knowledge_packages=knowledge_packages)
        knowledge_packages.errors = errors
        return knowledge_packages

    def __repr__(self) -> str:
        return "<{} Knowledge Packages>".format(len(self.knowledge_packages))


class ParentKnowledgePackageField(SystemField):
    """System field for access Knowledge Packages.

    Note:
        This class is based on ParentRecordAccessField from Invenio-RDM-Records.

    See:
        https://github.com/inveniosoftware/invenio-rdm-records/blob/4bddf95d3ca0b784c45746a5d2280c10824c9ca4/invenio_rdm_records/records/systemfields/access/field/record.py#L178
    """

    def __init__(
        self,
        key="knowledge_packages",
        knowledge_packages_obj_class=KnowledgePackageManager,
    ):
        """Initializer."""
        self._knowledge_packages_obj_class = knowledge_packages_obj_class
        super().__init__(key)

    def obj(self, instance):
        """Get the access object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        data = self.get_dictkey(instance)
        if data:
            obj = self._knowledge_packages_obj_class.from_dict(data)
        else:
            obj = self._knowledge_packages_obj_class()

        self._set_cache(instance, obj)
        return obj

    def set_obj(self, record, obj):
        """Set the access object."""
        if isinstance(obj, dict):
            obj = self._knowledge_packages_obj_class.from_dict(obj)

        assert isinstance(obj, self._knowledge_packages_obj_class)
        self._set_cache(record, obj)

    def __get__(self, record, owner=None):
        """Get the access object."""
        if record is None:
            return self

        return self.obj(record)

    def __set__(self, record, obj):
        """Get the access object."""
        self.set_obj(record, obj)

    def pre_commit(self, record):
        """Dump the configured values before the record is committed."""
        obj = self.obj(record)

        if obj is not None:
            # From the invenio-rdm-records:
            # only set the 'access' property if one was present in the
            # first place -- this was a problem in the unit test:
            # tests/resources/test_resources.py:test_simple_flow
            record["knowledge_packages"] = obj.dump()
