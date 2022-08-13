# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources component."""

from invenio_drafts_resources.services.records.components import ServiceComponent


class PackageResourceAccessComponent(ServiceComponent):
    """Component to validate and integrate packages and resources access."""

    def add_package_resource(
        self, identity, record=None, resource=None, relationship_type=None, **kwargs
    ):
        """Add resource to a package."""
        # copying access definitions from the package to the resource
        package_access = record["access"]
        resource.access.from_dict(package_access)
