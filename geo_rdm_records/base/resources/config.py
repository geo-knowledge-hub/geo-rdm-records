# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base resources configuration."""

from invenio_rdm_records.resources.config import (
    RDMRecordResourceConfig as BaseRecordResourceConfig,
)

from geo_rdm_records.base.resources.args import GEOSearchRequestArgsSchema


class BaseGEOResourceConfig(BaseRecordResourceConfig):
    """Record resource configuration."""

    request_search_args = GEOSearchRequestArgsSchema
