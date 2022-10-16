# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Context component."""

from invenio_drafts_resources.services.records.components import ServiceComponent


class PackageContextComponent(ServiceComponent):
    """Service component for the Package Context."""

    def context_associate_resource(self, identity, package=None, record=None, **kwargs):
        """Handle package/resource for the context association."""
        # we are using the parent to "simulate" a context
        # for the package.
        record.parent.relationship.managed_by = package.parent

    def context_dissociate_resource(
        self, identity, package=None, record=None, **kwargs
    ):
        """Handle package/resource for the context dissociation."""
        if record.parent.relationship.managed_by:
            # avoiding errors
            del record.parent.relationship.managed_by

    def context_update_access(self, identity, data=None, record=None, errors=None):
        """Update draft handler."""
        package_context_access = data.get("access", {})
        package_context_record_policy = package_context_access.get(
            "record_policy", None
        )

        if package_context_record_policy:
            if "access" in record.parent:
                record.parent.access.record_policy = package_context_record_policy
