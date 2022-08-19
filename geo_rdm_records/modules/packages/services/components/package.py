# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages component."""

from invenio_drafts_resources.services.records.components import ServiceComponent


class PackageComponent(ServiceComponent):
    """Service component for the ``Package`` handling."""

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        # Validation steps before publication
        # (This process must be implemented in a task).

        # 1. Check if package can be published

        # 2. Check if all resources can be published

        # 3. Reserve DOI for package

        # 4. Reserve DOI for resources

        # 5. Link the package metadata with the resources (via DOI)

        # 6. Link the resources' metadata with the package (via DOI)

        # 7. Publish the package

        # 8. Publish the resources

        # 9. Enable mint the DOIs

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        # ToDo: Must be implemented.
