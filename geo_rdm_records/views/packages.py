# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages UI Views."""

from flask import render_template
from flask_babelex import lazy_gettext as _

from geo_rdm_records.base.resources.decorators import pass_package_or_draft

RECORD_POLICY = [
    {
        "text": "Open",
        "value": "open",
        "icon": "group",
        "helpText": _("The records of your records can be public or private."),
    },
    {
        "text": "Closed",
        "value": "closed",
        "icon": "lock",
        "helpText": _("The records of your records can be private."),
    },
]


@pass_package_or_draft(serialize=True)
def packages_dashboard_versions(pid_value, package, package_ui):
    """Versions Dashboard page."""
    permissions = package.has_permissions_to(["update", "read"])

    endpoint = f"/api/packages/{pid_value}/versions"

    return render_template(
        "geo_rdm_records/packages/dashboard/versions.html",
        package=package_ui,
        # Tip from Invenio App RDM: Pass permissions so we can
        # disable partially UI components (e.g., Settings tab)
        permissions=permissions,
        active_package_header_menu_item="versions",
        endpoint=endpoint,
    )


@pass_package_or_draft(serialize=True)
def packages_dashboard_resources(pid_value, package, package_ui):
    """Resources Dashboard page."""
    permissions = package.has_permissions_to(["update", "read"])
    package_parent_id = package["parent"]["id"]

    endpoint = f"/api/packages/context/{package_parent_id}/resources"

    return render_template(
        "geo_rdm_records/packages/dashboard/resources.html",
        package=package_ui,
        permissions=permissions,
        active_package_header_menu_item="resources",
        endpoint=endpoint,
    )


@pass_package_or_draft(serialize=True)
def packages_dashboard_settings(pid_value, package, package_ui):
    """Settings Dashboard page."""
    permissions = package.has_permissions_to(["update", "read"])

    return render_template(
        "geo_rdm_records/packages/dashboard/settings/privileges.html",
        package=package_ui,
        permissions=permissions,
        active_package_header_menu_item="settings",
        active_settings_menu_item="privileges",
        form_config=dict(
            access=dict(record_policy=RECORD_POLICY),
        ),
    )


@pass_package_or_draft(serialize=True)
def packages_dashboard_members(pid_value, package, package_ui):
    """Settings Dashboard page."""
    permissions = package.has_permissions_to(["update", "read"])

    return render_template(
        "geo_rdm_records/packages/dashboard/members.html",
        package=package_ui,
        permissions=permissions,
        active_package_header_menu_item="members",
    )
