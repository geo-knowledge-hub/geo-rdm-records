# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Resources component."""

from .access import PackageResourceAccessComponent
from .integration import (
    PackageResourceCommunityComponent,
    PackageResourceIntegrationComponent,
)

__all__ = (
    "PackageResourceIntegrationComponent",
    "PackageResourceAccessComponent",
    "PackageResourceCommunityComponent",
)
