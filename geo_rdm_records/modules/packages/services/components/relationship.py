# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Relationship component."""


from invenio_drafts_resources.services.records.components import ServiceComponent


class PackageRelationshipComponent(ServiceComponent):
    """Service component for the ``relationship`` field."""

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        record.relationship = draft.get("relationship", {})

    def import_resources(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        # ToDo: Handle the  reference to the package in the resources available in the "relationship"
        draft.relationship = record.get("relationship", {})

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        draft.relationship = record.get("relationship", {})
