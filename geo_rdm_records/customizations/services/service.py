# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resource Service."""

from invenio_rdm_records.services import RDMRecordService as BaseRecordService
from invenio_records_resources.services import LinksTemplate
from invenio_search.engine import dsl


class GEORDMRecordService(BaseRecordService):
    """RDM Record service."""

    def search_package_records(
        self, identity, package_id, params=None, search_preference=None, **kwargs
    ):
        """Search for records associated with the given Package."""
        self.require_permission(identity, "read")

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search",
            identity,
            params,
            search_preference,
            record_cls=self.record_cls,
            search_opts=self.config.search_resource,
            extra_filter=dsl.Q("term", **{"relationship.packages.id": str(package_id)}),
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
        self, identity, package_id, params=None, search_preference=None, **kwargs
    ):
        """Search for drafts associated with the given Package."""
        self.require_permission(identity, "search_drafts")

        # Prepare and execute the search
        params = params or {}
        # For the resources, we must return all the content
        params.update(dict(allversions=True))

        search_result = self._search(
            "search_drafts",
            identity,
            params,
            search_preference,
            record_cls=self.draft_cls,
            search_opts=self.config.search_resource_drafts,
            extra_filter=dsl.Q("term", **{"relationship.packages.id": str(package_id)}),
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

    def search_package_context_versions(
        self, identity, package_parent_id, params=None, search_preference=None, **kwargs
    ):
        """Search for records and drafts associated with the given Package Context (Parent ID)."""
        self.require_permission(identity, "search_drafts")

        # Prepare and execute the search
        params = params or {}
        # For the resources, we must return all the content
        params.update(dict(allversions=True))

        search_result = self._search(
            "search_drafts",
            identity,
            params,
            search_preference,
            record_cls=self.draft_cls,
            search_opts=self.config.search_resource_drafts,
            extra_filter=dsl.Q(
                "term", **{"parent.relationship.managed_by.id": str(package_parent_id)}
            ),
            permission_action="read_draft",
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_package_context,
                context={"args": params, "id": package_parent_id},
            ),
            links_item_tpl=self.links_item_tpl,
        )
