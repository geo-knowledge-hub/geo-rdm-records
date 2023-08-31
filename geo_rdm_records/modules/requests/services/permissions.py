# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for GEO RDM Records (Requests API)."""

from geo_config.security.generators import GeoSecretariat
from invenio_records_permissions.policies.records import RecordPermissionPolicy


class RequestNotificationPermissionPolicy(RecordPermissionPolicy):
    """Permission policy for the request notification service."""

    can_notify = [GeoSecretariat()]
