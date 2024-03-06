# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services."""

from invenio_records_resources.services import LinksTemplate
from invenio_search.engine import dsl

from geo_rdm_records.base.services.links import MutableLinksTemplate
from geo_rdm_records.base.services.search import BaseSearchMultiIndexService


class SearchRecordService(BaseSearchMultiIndexService):
    """Search record specialized service."""

    #
    # Properties
    #
    @property
    def indices(self):
        """Search indices."""
        return self.config.indices

    @property
    def indices_draft(self):
        """Search indices (draft)."""
        return self.config.indices_draft

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

    #
    # High-level API
    #
    def search(
        self, identity, params=None, search_preference=None, expand=False, **kwargs
    ):
        """Search for records matching the querystring."""
        self.require_permission(identity, "search")

        # Prepare and execute the search
        params = params or {}
        search = self._search(
            "search",
            identity,
            params,
            search_preference,
            indices=self.indices,
            **kwargs,
        )
        search_result = search.execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(self.config.links_search, context={"args": params}),
            links_item_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def search_drafts(
        self, identity, params=None, search_preference=None, expand=False, **kwargs
    ):
        """Search for drafts records matching the querystring."""
        self.require_permission(identity, "search_drafts")

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search_drafts",
            identity,
            params,
            search_preference,
            record_cls=self.draft_cls,
            search_opts=self.config.search_drafts,
            # `has_draft` systemfield is not defined here. This is not ideal
            # but it helps avoid overriding the method. See how is used in
            # https://github.com/inveniosoftware/invenio-rdm-records
            extra_filter=dsl.Q("term", has_draft=False),
            permission_action="read_draft",
            indices=self.indices_draft,
            **kwargs,
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_drafts, context={"args": params}
            ),
            links_item_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def search_community_records(
        self, identity, community_id, params=None, search_preference=None, **kwargs
    ):
        """Search for records published in the given community."""
        self.require_permission(identity, "read")

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search",
            identity,
            params,
            search_preference,
            search_opts=self.config.search,
            extra_filter=dsl.Q("term", **{"parent.communities.ids": str(community_id)}),
            permission_action="read",
            indices=self.indices,
            **kwargs,
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_community_records,
                context={
                    "args": params,
                    "id": community_id,
                },
            ),
            links_item_tpl=self.links_item_tpl,
        )
