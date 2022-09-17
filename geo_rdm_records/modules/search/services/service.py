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
from invenio_records_resources.config import lt_es7
from invenio_search import current_search_client

from .links import MutableLinksTemplate


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
            index=self.indices[0],  # enabling multiple indices search
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
        if not lt_es7:
            extras["track_total_hits"] = True
        search = search.extra(**extras)

        return search
