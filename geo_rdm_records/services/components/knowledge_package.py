# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from invenio_pidstore.errors import PIDUnregistered

from invenio_drafts_resources.services.records.components import ServiceComponent


class KnowledgePackageComponent(ServiceComponent):
    """Service component for Knowledge Package control."""

    def _get_ids(self, data=None):
        """Get the Knowledge Packages IDs from a Metadata document."""
        if data:
            parent_data = data.get("parent", {})
            return parent_data.get("knowledge_packages", [])

    def _check_record(self, identity, ids):
        """Check the record to be used as a Knowledge Package.

        This function validate if the record (`ids`) can be used as a Knowledge Package
        of another record.

        Args:
            identity (flask_principal.Identity): User Identity

            ids (List[str]): List of Knowledge Record IDs to be validated.

        Returns:
            None

        Raises:
            ValidationError: when the record can be used as a Knowledge Package.

            PermissionDeniedError: when the record can't be accessed by the user.
        """
        # record managers = `owners`, `system process`, `community currator`
        for id_ in ids:

            try:
                record = self.service.draft_cls.pid.resolve(id_, registered_only=False)
            except PIDUnregistered:
                record = self.service.record_cls.pid.resolve(id_)

            # checking the permission
            self.service.require_permission(identity, "manage", record=record)

    def _populate_knowledge_packages(self, identity, data=None, record=None, **kwargs):
        """Populate the Knowledge Package field.

        This function validate the IDs defined to be used as a Knowledge Packages and save
        them into the Record (`knowledge_package` field).
        """
        ids = self._get_ids(data)

        if ids:
            self._check_record(identity, ids=ids)
            record.parent.knowledge_packages.refresh_from_dict(
                knowledge_packages_dict=ids
            )

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject Knowledge Package references to the record."""
        self._populate_knowledge_packages(identity, data, record, **kwargs)

    def update_draft(self, identity, data=None, record=None, errors=None, **kwargs):
        """Inject Knowledge Package references to the record."""
        self._populate_knowledge_packages(identity, data, record, **kwargs)

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        self._populate_knowledge_packages(identity, draft, record, **kwargs)

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        self._populate_knowledge_packages(identity, record, draft, **kwargs)

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        self._populate_knowledge_packages(identity, record, draft, **kwargs)
