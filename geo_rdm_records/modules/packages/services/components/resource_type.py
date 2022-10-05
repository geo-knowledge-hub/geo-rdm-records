# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Package Type component."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_records.dictutils import dict_set


class PackageResourceTypeComponent(ServiceComponent):
    """Component to manage Package resource type."""

    def _fix_resource_type(self, obj):
        """Fix the resource type of the package."""
        metadata = obj.get("metadata", {})
        dict_set(metadata, "resource_type", {"id": "knowledge"})

        return metadata

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        metadata_fixed = self._fix_resource_type(data)
        record.metadata = metadata_fixed

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        metadata_fixed = self._fix_resource_type(data)
        record.metadata = metadata_fixed

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        metadata_fixed = self._fix_resource_type(draft)
        record.metadata = metadata_fixed

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        metadata_fixed = self._fix_resource_type(record)
        draft.metadata = metadata_fixed

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        metadata_fixed = self._fix_resource_type(record)
        draft.metadata = metadata_fixed
