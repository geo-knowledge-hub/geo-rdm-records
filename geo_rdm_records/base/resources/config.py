# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base resources configuration."""

from copy import deepcopy

from flask_resources import ResponseHandler
from invenio_rdm_records.resources import config as rdm_resources_config
from invenio_rdm_records.resources.config import (
    RDMRecordResourceConfig as BaseRecordResourceConfig,
)

from geo_rdm_records.base.resources.args import GEOSearchRequestArgsSchema
from geo_rdm_records.base.resources.serializers import UIRecordJSONSerializer

#
# Response handlers
#
record_serializers = deepcopy(rdm_resources_config.record_serializers)
record_serializers.update(
    {"application/vnd.inveniordm.v1+json": ResponseHandler(UIRecordJSONSerializer())}
)


class BaseGEOResourceConfig(BaseRecordResourceConfig):
    """Record resource configuration."""

    # Resource routes
    response_handlers = record_serializers

    request_search_args = GEOSearchRequestArgsSchema
