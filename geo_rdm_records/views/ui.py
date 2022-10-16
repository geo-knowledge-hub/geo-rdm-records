# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records UI Views."""

from flask import Blueprint, current_app, render_template
from flask_babelex import lazy_gettext as _
from flask_login import current_user
from flask_menu import current_menu
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError

from ..searchapp import search_app_context
from . import packages as packages_ui


#
# Error handlers
#
def not_found_error(error):
    """Handler for 'Not Found' errors."""
    return render_template(current_app.config["THEME_404_TEMPLATE"]), 404


def record_permission_denied_error(error):
    """Handle permission denier error on record views."""
    if not current_user.is_authenticated:
        # trigger the flask-login unauthorized handler
        return current_app.login_manager.unauthorized()
    return render_template(current_app.config["THEME_403_TEMPLATE"]), 403


#
# UI blueprints
#
def create_ui_blueprint(app):
    """Register blueprint routes on app."""
    routes = app.config["GEO_RDM_PACKAGES_ROUTES"]

    blueprint = Blueprint(
        "geo_rdm_records",
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    blueprint.add_url_rule(
        routes["package-dashboard-versions"],
        view_func=packages_ui.packages_dashboard_versions,
    )

    blueprint.add_url_rule(
        routes["package-dashboard-resources"],
        view_func=packages_ui.packages_dashboard_resources,
    )

    blueprint.add_url_rule(
        routes["package-dashboard-members"],
        view_func=packages_ui.packages_dashboard_members,
    )

    blueprint.add_url_rule(
        routes["package-dashboard-settings"],
        view_func=packages_ui.packages_dashboard_settings,
    )

    @blueprint.before_app_first_request
    def register_menus():
        """Register community menu items."""
        packages = current_menu.submenu("packages")

        packages.submenu("versions").register(
            "geo_rdm_records.packages_dashboard_versions",
            text=_("Versions"),
            order=1,
            expected_args=["pid_value"],
            **dict(icon="code branch", permissions=True)
        )

        packages.submenu("resources").register(
            "geo_rdm_records.packages_dashboard_resources",
            text=_("Resources"),
            order=2,
            expected_args=["pid_value"],
            **dict(icon="boxes", permissions=True)
        )

        packages.submenu("members").register(
            "geo_rdm_records.packages_dashboard_members",
            text=_("Members"),
            order=3,
            expected_args=["pid_value"],
            **dict(icon="users", permissions=True)
        )

        packages.submenu("settings").register(
            "geo_rdm_records.packages_dashboard_settings",
            text=_("Settings"),
            order=4,
            expected_args=["pid_value"],
            **dict(icon="cogs", permissions=True)
        )

    # Register error handlers
    blueprint.register_error_handler(
        PermissionDeniedError, record_permission_denied_error
    )
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)

    # Register context processor
    blueprint.app_context_processor(search_app_context)

    return blueprint
