# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Requests service config module."""

from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    ServiceConfig,
)

from .permissions import RequestNotificationPermissionPolicy


class RequestNotificationServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Assistance Requests for Packages Service config."""

    # Common configuration
    service_id = "requests-notification"
    permission_policy_cls = RequestNotificationPermissionPolicy
