# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Relationship component."""

from invenio_drafts_resources.services.records.components import ServiceComponent

from geo_rdm_records.proxies import current_geo_packages_service


class ResourceRelationshipComponent(ServiceComponent):
    """Service component for the ``relationship`` field."""

    #
    # Auxiliary methods
    #
    def _read_relationship(self, data):
        """Read relationship from the data dictionary."""
        return data.get("parent", {}).get("relationship", {}) if data else {}

    #
    # Component methods
    #
    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed relationship to the record."""
        # ToDo: Review
        record.parent.relationship = self._read_relationship(data)

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        record.relationship = draft.get("relationship", {})

    def edit(self, identity, draft=None, record=None):
        """Edit a record handler."""
        draft.relationship = record.get("relationship", {})

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete draft handler."""
        if draft:
            draft_id = draft.get("id")
            packages = draft.get("relationship", {}).get("packages", [])

            if draft_id and packages:
                package_id = packages[0]["id"]

                current_geo_packages_service.resource_delete(
                    identity, package_id, dict(resources=[{"id": draft_id}])
                )
