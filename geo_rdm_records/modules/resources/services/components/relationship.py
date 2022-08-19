# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Relationship component."""

from copy import copy

from invenio_drafts_resources.services.records.components import ServiceComponent


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
        record.parent.relationship = self._read_relationship(data)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed relationship to the record."""
        record.parent.relationship = self._read_relationship(data)

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        record.parent.relationship = draft.parent.relationship

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        record.parent.relationship = draft.parent.relationship

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        record.parent.relationship = draft.parent.relationship
