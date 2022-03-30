# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from flask_babelex import gettext as _

from . import config


class GEORDMRecords(object):
    """GEO Knowledge Hub Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["geo-rdm-records"] = self

    def init_config(self, app):
        """Initialize configuration."""
        supported_configurations = [
            "RDM_RECORD_CLS",
            "RDM_DRAFT_CLS",
            "RDM_RECORD_SCHEMA_CLS",
            "RDM_RECORD_PARENT_SCHEMA_CLS",
            "RDM_RECORD_SECRET_LINK_CLS",
            "RDM_PERMISSION_POLICY",
            "RDM_FACETS"
        ]
        for k in dir(config):
            if k in supported_configurations or k.startswith("GEO_RDM_"):
                app.config.setdefault(k, getattr(config, k))
