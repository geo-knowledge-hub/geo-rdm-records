# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Requests service."""

from invenio_drafts_resources.services.records import RecordService
from invenio_requests import current_requests_service
from invenio_search.engine import dsl


class BaseRequestService(RecordService):
    """Base request service."""

    #
    # Request type
    #
    request_type = None

    #
    # Topic type
    #
    request_topic_type = None

    #
    # Auxiliary method
    #
    def _search_record_requests(self, identity, record_pid, extra_filter=None):
        """Search for requests related to a record.

        Args:
            identity: User identity.

            record_pid: Record PID to be used as reference to load requests.

            extra_filter: Extra filters to get the requests.

        Note:
            This is an initial implementation. In a future version, the rdm records module
            will be able the 'record requests' search. Maybe, we can use this.
        """
        topic_type = f"topic.{self.request_topic_type}"

        # defining the filter
        filter_ = dsl.query.Bool(
            "must",
            must=[
                dsl.Q("term", **{topic_type: record_pid}),
            ],
        )

        if extra_filter:
            filter_ = filter_ & extra_filter

        # search
        search_result = current_requests_service.search(
            identity=identity, extra_filter=filter_
        ).to_dict()

        return search_result["hits"]["hits"]
