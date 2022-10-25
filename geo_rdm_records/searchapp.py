# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration helper for React-Searchkit."""

from functools import partial

from flask import current_app
from invenio_search_ui.searchconfig import search_app_config


def search_app_context():
    """Search app context processor."""
    return {
        "search_app_packages_versions": partial(
            search_app_config,
            config_name="GEO_RDM_PACKAGES_VERSION_SEARCH",
            available_facets=current_app.config["RDM_FACETS"],
            sort_options=current_app.config["RDM_SORT_OPTIONS"],
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
            initial_filters=["allversions", "true"],
        ),
        "search_app_packages_resources": partial(
            search_app_config,
            config_name="GEO_RDM_PACKAGES_RESOURCES_SEARCH",
            available_facets=current_app.config["RDM_FACETS"],
            sort_options=current_app.config["RDM_SORT_OPTIONS"],
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        ),
    }
