# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Relationship component."""

from copy import copy

from invenio_drafts_resources.services.records.components import ServiceComponent


class RelationshipComponent(ServiceComponent):
    """Service component for the ``relationship`` field."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed relationship to the record."""
        record.relationship = data.get("relationship", {})

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed relationship to the record."""
        record.relationship = data.get("relationship", {})

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        record.relationship = draft.get("relationship", {})

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        draft.relationship = record.get("relationship", {})

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        draft.relationship = copy(record.get("relationship", {}))
