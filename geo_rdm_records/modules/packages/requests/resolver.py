# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources requests resolver."""

from geo_rdm_records.base.requests import BaseRecordProxy, BaseRecordResolver

from ..records.api import GEOPackageDraft, GEOPackageRecord


class RecordProxy(BaseRecordProxy):
    """Proxy for draft or record classes."""

    record_cls = GEOPackageRecord

    draft_cls = GEOPackageDraft


class RecordResolver(BaseRecordResolver):
    """Record entity resolver."""

    type_id = "packages"

    record_cls = GEOPackageDraft

    proxy_cls = RecordProxy

    service_id = "records_package"

    type_key = "package"
