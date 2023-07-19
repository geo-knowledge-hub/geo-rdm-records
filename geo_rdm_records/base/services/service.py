# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base Mixin service classes."""

from invenio_rdm_records.services.services import RDMRecordService as BaseRecordService
from invenio_records_resources.services import LinksTemplate
from invenio_search.engine import dsl
from sqlalchemy.orm.exc import NoResultFound


class BaseRDMService(BaseRecordService):
    """Service class for GEO RDM Records services (Based on Invenio RDM Records service)."""

    # ToDo: Experimental
    #       Search methods for packages. At this moment, I think will be required to implement
    #       the methods again!
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
            extra_filter=dsl.Q("term", has_draft=False)
            & dsl.Q("term", **{"parent.type": self.config.search_type}),
            permission_action="read_draft",
            **kwargs
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

    def search_versions(
        self, identity, id_, params=None, search_preference=None, expand=False, **kwargs
    ):
        """Search for record's versions."""
        try:
            record = self.record_cls.pid.resolve(id_, registered_only=False)
        except NoResultFound:
            record = self.draft_cls.pid.resolve(id_, registered_only=False)

        self.require_permission(identity, "read", record=record)

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search_versions",
            identity,
            params,
            search_preference,
            record_cls=self.record_cls,
            search_opts=self.config.search_versions,
            extra_filter=dsl.Q(
                "term", **{"parent.id": str(record.parent.pid.pid_value)}
            )
            & dsl.Q("term", **{"parent.type": self.config.search_type}),
            permission_action="read",
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_versions, context={"id": id_, "args": params}
            ),
            links_item_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def search(
        self, identity, params=None, search_preference=None, expand=False, **kwargs
    ):
        """Search for records matching the querystring."""
        extra_filter = dsl.Q("term", **{"parent.type": self.config.search_type})

        if "extra_filter" in kwargs:
            kwargs["extra_filter"] = kwargs["extra_filter"] & extra_filter

        else:
            kwargs["extra_filter"] = extra_filter

        return super().search(identity, params, search_preference, expand, **kwargs)
