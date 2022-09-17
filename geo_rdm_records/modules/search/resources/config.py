# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Search resources configuration."""

from geo_rdm_records.base.resources.config import BaseGEOResourceConfig


class SearchRecordResourceConfig(BaseGEOResourceConfig):
    """Search record resource config."""

    # Blueprint configuration
    blueprint_name = "records_search"
    url_prefix = "/search"

    routes = {"list": ""}
