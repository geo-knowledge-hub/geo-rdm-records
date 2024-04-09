# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 - 2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Base search services."""

from invenio_drafts_resources.services.records.service import (
    RecordService as BaseRecordService,
)
from invenio_rdm_records.services import RDMRecordService as BaseRDMRecordService
from invenio_records_permissions.api import permission_filter
from invenio_records_resources.services import LinksTemplate
from invenio_search import current_search_client


class BaseSearchMultiIndexService(BaseRecordService):
    """Search records across multiple indices."""

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
        index=None,
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
            index=indices
            or record_cls.index.search_alias,  # enabling multiple indices search
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
        index=None,
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


class BaseRelatedRecordsSearchService(
    BaseRDMRecordService, BaseSearchMultiIndexService
):
    """Search service with `more like this` support."""

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

        # Search for the latest version of the package,
        # avoiding duplications and old versions
        search = search.query(
            "bool",
            must=[
                {
                    "more_like_this": {
                        "fields": self.config.fields_more_like_this,
                        "like": {"_id": record.id},
                        "min_term_freq": 5,
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
