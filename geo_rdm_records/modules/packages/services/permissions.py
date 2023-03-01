# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Permissions."""

from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy


class PackagesPermissionPolicy(BaseGEOPermissionPolicy):
    """Access control configuration for records."""

    #
    # High-level permissions (used by low-level)
    #
    can_manage = BaseGEOPermissionPolicy.can_manage
    can_curate = BaseGEOPermissionPolicy.can_curate

    #
    # Package Context
    #
    can_context_update_access = can_curate
    can_context_associate_resource = can_curate
    can_context_dissociate_resource = can_curate
