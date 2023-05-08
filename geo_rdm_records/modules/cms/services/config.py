# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records CMS service config module."""

from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfig,
    ServiceConfig,
)

from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy


class CMSServiceConfig(ServiceConfig, ConfiguratorMixin):
    """CMS Service config."""

    # Common configuration
    service_id = "cms"
    permission_policy_cls = BaseGEOPermissionPolicy

    # CMS configuration
    cms_api_token = FromConfig("GEO_RDM_RECORDS_CMS_API_TOKEN", import_string=False)
    cms_api_address = FromConfig("GEO_RDM_RECORDS_CMS_API_ADDRESS", import_string=False)
