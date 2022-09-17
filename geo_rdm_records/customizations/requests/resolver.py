# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources requests resolver."""

from geo_rdm_records.base.requests import BaseRecordProxy, BaseRecordResolver

from ..records.api import GEODraft, GEORecord


class RecordProxy(BaseRecordProxy):
    """Proxy for draft or record classes."""

    record_cls = GEORecord

    draft_cls = GEODraft


class RecordResolver(BaseRecordResolver):
    """Record entity resolver."""

    type_id = "resources"

    record_cls = GEODraft

    proxy_cls = RecordProxy

    service_id = "records"
