# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources Communities."""

from invenio_drafts_resources.services.records.components import ServiceComponent


class PackageResourceCommunitiesComponent(ServiceComponent):
    """Service component for the ``communities`` field managed by packages."""

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        # 1. Checking if the resource is associated with a package
        #    Note: In the current version, the `managed by` returns
        #          the package parent (used as a context for the resources)
        package_parent = record.parent.relationship.managed_by

        if package_parent:
            # 2. Copy community from the package parent (context)
            record.parent.communities.from_dict(package_parent.communities.to_dict())
