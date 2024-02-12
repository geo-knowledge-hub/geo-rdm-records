# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Service."""

from invenio_rdm_records.services import RDMRecordService as BaseRecordService

from geo_rdm_records.base.services.links import MutableLinksTemplate


class GEOMarketplaceItemService(BaseRecordService):
    """GEO Marketplace Item Service."""

    #
    # Properties
    #
    @property
    def links_item_tpl(self):
        """Item links template."""
        return MutableLinksTemplate(
            self.config.links_item, self.config.links_registry_type
        )
