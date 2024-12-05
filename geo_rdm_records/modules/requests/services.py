# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Service handler."""

from flask_babelex import lazy_gettext as _
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord

from geo_rdm_records.modules.marketplace.records.api import (
    GEOMarketplaceItem,
    GEOMarketplaceItemDraft,
)
from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)
from geo_rdm_records.modules.rdm import GEODraft, GEORecord
from geo_rdm_records.proxies import (
    current_geo_packages_service,
    current_marketplace_service,
)


class ServiceHandler:
    """Service handler class for actions.

    This class add the support for multiple ``services`` based on
    different classes. This implementation was created to support
    the use of the same set of actions with multiple services and
    entities.

    ToDo:
        This is the best approach ? Do Invenio Requests provide
        another way to handle this ?
    """

    services = [
        {
            "classes": (GEODraft, GEORecord, RDMDraft, RDMRecord),
            "service": current_rdm_records_service,
        },
        {
            "classes": (GEOPackageDraft, GEOPackageRecord),
            "service": current_geo_packages_service,
        },
        {
            "classes": (GEOMarketplaceItem, GEOMarketplaceItemDraft),
            "service": current_marketplace_service,
        },
    ]
    """Definition of the services available to handle actions."""

    def _get_service(self, record):
        """Select the service.

        Select the service based on the ``record`` type.
        """
        for service in self.services:
            if isinstance(record, tuple(service["classes"])):
                return service["service"]

        raise ValueError(_("Invalid record type."))
