# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper proxy to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

current_geo_rdm_records = LocalProxy(lambda: current_app.extensions["geo-rdm-records"])
"""Helper proxy to get the current RDM-Records extension."""

current_geo_packages_service = LocalProxy(
    lambda: current_app.extensions["geo-rdm-records"].packages_service
)
"""Helper proxy to get the current Packages API service."""
