# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Relationship component."""


from invenio_drafts_resources.services.records.components import ServiceComponent


class HarvesterComponent(ServiceComponent):
    """Service component for the ``harvester`` field."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        record["harvester"] = data.get("harvester", {})

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        record["harvester"] = draft.get("harvester", {})
