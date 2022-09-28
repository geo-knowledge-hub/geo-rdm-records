# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resource Service."""

from elasticsearch_dsl.query import Q
from invenio_rdm_records.services import RDMRecordService as BaseRecordService
from invenio_records_resources.services import LinksTemplate


class GEORDMRecordService(BaseRecordService):
    """RDM Record service."""

    def search_package_records(
        self, identity, package_id, params=None, es_preference=None, **kwargs
    ):
        """Search for records associated with the given Package."""
        self.require_permission(identity, "read")

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search",
            identity,
            params,
            es_preference,
            record_cls=self.record_cls,
            search_opts=self.config.search_resource,
            extra_filter=Q(
                "term", **{"parent.relationship.managed_by.id": str(package_id)}
            ),
            permission_action="read",
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_package_records,
                context={"args": params, "id": package_id},
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def search_package_drafts(
        self, identity, package_id, params=None, es_preference=None, **kwargs
    ):
        """Search for drafts associated with the given Package."""
        self.require_permission(identity, "search_drafts")

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search_drafts",
            identity,
            params,
            es_preference,
            record_cls=self.draft_cls,
            search_opts=self.config.search_resource_drafts,
            extra_filter=Q(
                "term", **{"parent.relationship.managed_by.id": str(package_id)}
            )
            & Q("term", has_draft=False),
            permission_action="read_draft",
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_package_drafts,
                context={"args": params, "id": package_id},
            ),
            links_item_tpl=self.links_item_tpl,
        )
