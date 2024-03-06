# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Service."""

from invenio_rdm_records.services import RDMRecordService as BaseRecordService
from invenio_records_resources.services import LinksTemplate

from geo_rdm_records.base.services.search import BaseSearchMultiIndexService


class GEOMarketplaceItemService(BaseRecordService, BaseSearchMultiIndexService):
    """GEO Marketplace Item Service."""

    #
    # Properties
    #
    @property
    def indices_more_like_this(self):
        """Search indices."""
        return self.config.indices_more_like_this

    #
    # Initializer
    #
    def __init__(
        self,
        config,
        files_service=None,
        draft_files_service=None,
        secret_links_service=None,
        review_service=None,
    ):
        """Initializer."""
        super().__init__(config, files_service, draft_files_service)
        self._secret_links = secret_links_service
        self._review = review_service

    #
    # High-level API
    #
    def search_more_like_this(self, identity, _id, **extras):
        """Search content related to a record (more like this query)."""
        record = self.record_cls.pid.resolve(_id)

        self.require_permission(identity, "search")
        self.require_permission(identity, "read", record=record)

        search = self.create_search(
            identity,
            self.record_cls,
            self.config.search,
            permission_action="read",
            preference=None,
            indices=self.config.indices_more_like_this,
        )

        search = search.query(
            "bool",
            must=[
                {
                    "more_like_this": {
                        "fields": [
                            "metadata.title",
                            "metadata.description",
                            "metadata.subjects.subject",
                            "metadata.subjects.subject.keyword",
                            "metadata.additional_titles.title",
                            "metadata.additional_descriptions.description",
                            "metadata.related_identifiers.description",
                        ],
                        "like": {"_id": record.id},
                        "min_term_freq": 10,
                        "max_query_terms": 50,
                    }
                }
            ],
            filter=[{"term": {"versions.is_latest": True}}],
        )

        search = search.extra(**extras)
        search_result = search.execute()

        return self.result_list(
            self,
            identity,
            search_result,
            links_tpl=LinksTemplate(self.config.links_search),
            links_item_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=True,
        )
