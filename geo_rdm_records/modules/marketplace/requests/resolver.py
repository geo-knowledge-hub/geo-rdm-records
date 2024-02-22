# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources requests resolver."""

from geo_rdm_records.base.requests import BaseRecordProxy, BaseRecordResolver

from ..records.api import GEOMarketplaceItem, GEOMarketplaceItemDraft


class RecordProxy(BaseRecordProxy):
    """Proxy for draft or record classes."""

    record_cls = GEOMarketplaceItem

    draft_cls = GEOMarketplaceItemDraft


class MarketplaceItemDraftResolver(BaseRecordResolver):
    """Marketplace Item draft entity resolver."""

    type_id = "marketplace-items"

    record_cls = GEOMarketplaceItemDraft

    proxy_cls = RecordProxy

    service_id = "marketplace_items"

    type_key = "marketplace_item"


class MarketplaceItemResolver(BaseRecordResolver):
    """Marketplace Item entity resolver."""

    type_id = "marketplace-item-record"

    record_cls = GEOMarketplaceItem

    proxy_cls = RecordProxy

    service_id = "marketplace_items"

    type_key = "marketplace_item_record"
