# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resources configuration."""

from invenio_rdm_records.resources.config import (
    RDMRecordResourceConfig as BaseRecordResourceConfig,
)

from geo_rdm_records.base.resources import BaseGEOResourceConfig


class GEORecordResourceConfig(BaseGEOResourceConfig):
    """Record resource configuration."""

    # Resource routes
    routes = BaseRecordResourceConfig.routes

    # Packages API Routes

    # Package resources endpoint
    routes["item-resources-search"] = "/packages/<pid_value>/resources"

    # Draft Packages resources endpoint
    routes["item-draft-resources-search"] = "/packages/<pid_value>/draft/resources"
