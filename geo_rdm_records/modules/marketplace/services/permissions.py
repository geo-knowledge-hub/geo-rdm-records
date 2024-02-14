# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace service permissions."""

from invenio_records_permissions.generators import Disable

from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy


class MarketplacePermissionPolicy(BaseGEOPermissionPolicy):
    """Access control configuration for marketplace items."""

    #
    # Disabled actions (these should not be used or changed)
    #
    # Marketplace Items can not have DOIs.
    can_pid_create = [Disable()]
    can_pid_register = [Disable()]
    can_pid_update = [Disable()]
    can_pid_discard = [Disable()]
    can_pid_delete = [Disable()]
