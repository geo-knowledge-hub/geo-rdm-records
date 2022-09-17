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
        package = record.parent.relationship.managed_by

        if package:
            # 2. Copy the package community definition to the resource
            record.parent.communities.from_dict(package.parent.communities.to_dict())
