# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Service configuration."""

from geo_rdm_records.services.config import (
    GEORecordServiceConfig as BaseRecordServiceConfig,
)

from ..records.api import GEOPackageRecord, GEOPackageDraft

from .schemas import GEOPackageRecordSchema


class GEOPackageRecordServiceConfig(BaseRecordServiceConfig):
    """GEO Package record draft service config."""

    # Record and draft classes
    record_cls = GEOPackageRecord
    draft_cls = GEOPackageDraft

    # Schemas
    schema = GEOPackageRecordSchema
