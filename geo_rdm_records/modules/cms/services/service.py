# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records CMS service module."""

from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import TaskOp, unit_of_work
from invenio_requests.proxies import current_events_service

from geo_rdm_records.modules.cms.tasks import create_feed_post


class CMSService(Service):
    """CMS Service."""

    #
    # Properties
    #
    @property
    def _cms_api(self):
        """CMS API."""
        return self.config.cms_api_address

    @property
    def _cms_token(self):
        """CMS API Token."""
        return self.config.cms_api_token

    @unit_of_work()
    def create_feed_post(self, identity, request, uow):
        """Create a feed post."""
        self.require_permission(identity, "accept_request")

        # Searching for the basics body of the field
        search_result = current_events_service.search(identity, request.id)
        search_result = search_result.to_dict()

        # Temporary approach: Assuming that the event is the body of the feed.
        # ToDo: Review this approach to something more general
        feed_body = search_result["hits"]["hits"][0]
        feed_body = feed_body["payload"]["content"]

        # Preparing the feed post
        data = dict(title=request["title"].replace("Feed: ", ""), description=feed_body)

        # Registering tasks
        # ToDo: Include e-mail task to notify the GEO Secretariat users.
        uow.register(TaskOp(create_feed_post, self._cms_api, self._cms_token, data))

        # ToDo: Improve this return to provide more
        #       details of the operation performed.
        return True
