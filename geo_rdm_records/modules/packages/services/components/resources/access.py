# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources component."""

from invenio_drafts_resources.services.records.components import ServiceComponent

from geo_rdm_records.modules.packages.records.api import PackageRelationship


class PackageResourceAccessComponent(ServiceComponent):
    """Component to validate and integrate packages and resources access."""

    def package_add_resource(
        self, identity, package=None, resource=None, relationship_type=None, **kwargs
    ):
        """Add resource to a package."""
        if relationship_type == PackageRelationship.MANAGED.value:
            resource.access = package.get("access", {})
