# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services."""

from invenio_rdm_records.services.services import RDMRecordService as BaseRecordService

from geo_rdm_records.base.services.links import MutableLinksTemplate


class SearchRecordService(BaseRecordService):
    """Search record specialized service."""

    #
    # Properties
    #
    @property
    def links_item_tpl(self):
        """Item links template."""
        return MutableLinksTemplate(
            self.config.links_item, self.config.links_registry_type
        )

    @property
    def results_registry_type(self):
        """Registry class for records."""
        return self.config.results_registry_type
