# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services."""

from invenio_drafts_resources.services.records.service import (
    RecordService as BaseRecordService,
)
from invenio_records_permissions.api import permission_filter
from invenio_records_resources.services import LinksTemplate
from invenio_search import current_search_client
from invenio_search.engine import dsl

from geo_rdm_records.base.services.links import MutableLinksTemplate


class SearchRecordService(BaseRecordService):
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
    # Auxiliary methods
    #

    def create_search(
        self,
        identity,
        record_cls,
        search_opts,
        permission_action="read",
        preference=None,
        extra_filter=None,
        indices=None,
    ):
        """Instantiate a search class."""
        if permission_action:
            permission = self.permission_policy(
                action_name=permission_action, identity=identity
            )
        else:
            permission = None

        default_filter = permission_filter(permission)
        if extra_filter is not None:
            default_filter = default_filter & extra_filter

        search = search_opts.search_cls(
            using=current_search_client,
            default_filter=default_filter,
            index=indices,  # enabling multiple indices search
        )

        search = (
            search
            # Avoid query bounce problem
            .with_preference_param(preference)
            # Add document version to ES response
            .params(version=True)
        )

        # Extras
        extras = {}
        extras["track_total_hits"] = True
        search = search.extra(**extras)

        return search

    def search_request(
        self,
        identity,
        params,
        record_cls,
        search_opts,
        preference=None,
        extra_filter=None,
        permission_action="read",
        indices=None,
    ):
        """Factory for creating a Search DSL instance."""
        search = self.create_search(
            identity,
            record_cls,
            search_opts,
            permission_action=permission_action,
            preference=preference,
            extra_filter=extra_filter,
            indices=indices,
        )

        # Run search args evaluator
        for interpreter_cls in search_opts.params_interpreters_cls:
            search = interpreter_cls(search_opts).apply(identity, search, params)

        return search

    def _search(
        self,
        action,
        identity,
        params,
        search_preference,
        record_cls=None,
        search_opts=None,
        extra_filter=None,
        permission_action="read",
        indices=None,
        **kwargs,
    ):
        """Create the Elasticsearch DSL."""
        # Merge params
        # NOTE: We allow using both the params variable, as well as kwargs. The
        # params is used by the resource, and kwargs is used to have an easier
        # programatic interface .search(idty, q='...') instead of
        # .search(idty, params={'q': '...'}).
        params.update(kwargs)

        # Create an Elasticsearch DSL
        search = self.search_request(
            identity,
            params,
            record_cls or self.record_cls,
            search_opts or self.config.search,
            preference=search_preference,
            extra_filter=extra_filter,
            permission_action=permission_action,
            indices=indices,
        )

        # Run components
        for component in self.components:
            if hasattr(component, action):
                search = getattr(component, action)(identity, search, params)
        return search

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
