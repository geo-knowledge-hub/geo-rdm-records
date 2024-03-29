# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Views."""

from .api import (
    blueprint,
    create_draft_files_api_blueprint,
    create_marketplace_api_blueprint,
    create_marketplace_draft_files_api_blueprint,
    create_marketplace_files_api_blueprint,
    create_packages_api_blueprint,
    create_packages_context_api_blueprint,
    create_packages_files_api_blueprint,
    create_parent_links_api_blueprint,
    create_search_records_api_blueprint,
)
from .ui import create_ui_blueprint

__all__ = (
    # API
    "blueprint",
    "create_draft_files_api_blueprint",
    "create_packages_api_blueprint",
    "create_packages_files_api_blueprint",
    "create_parent_links_api_blueprint",
    "create_search_records_api_blueprint",
    "create_packages_context_api_blueprint",
    "create_marketplace_api_blueprint",
    "create_marketplace_files_api_blueprint",
    "create_marketplace_draft_files_api_blueprint",
    # UI
    "create_ui_blueprint",
)
