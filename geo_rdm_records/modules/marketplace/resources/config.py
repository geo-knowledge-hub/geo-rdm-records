# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Resource config."""

from copy import deepcopy

from flask_resources import ResponseHandler
from invenio_rdm_records.resources import config as rdm_resources_config

from geo_rdm_records.base.resources import BaseGEOResourceConfig
from geo_rdm_records.base.resources.serializers import UIRecordJSONSerializer

#
# Response handlers
#
record_serializers = deepcopy(rdm_resources_config.record_serializers)
record_serializers.update(
    {"application/vnd.inveniordm.v1+json": ResponseHandler(UIRecordJSONSerializer())}
)


class GEOMarketplaceItemResourceConfig(BaseGEOResourceConfig):
    """GEO Marketplace Item resource config."""

    blueprint_name = "marketplace-items"
    url_prefix = "/marketplace/items"

    # Response handlers
    response_handlers = record_serializers
