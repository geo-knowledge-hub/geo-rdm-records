# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records API Views."""

from flask import Blueprint

blueprint = Blueprint("geo_rdm_records_ext", __name__, template_folder="../templates")


@blueprint.record_once
def init(state):
    """Init app."""
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    rr_ext = app.extensions["invenio-records-resources"]
    idx_ext = app.extensions["invenio-indexer"]
    ext = app.extensions["geo-rdm-records"]

    # services - packages
    rr_ext.registry.register(ext.service, service_id="records_package")
    rr_ext.registry.register(ext.service.files, service_id="files_package")
    rr_ext.registry.register(ext.service.draft_files, service_id="files_package_draft")

    # services - marketplace
    rr_ext.registry.register(ext.service_marketplace, service_id="marketplace_items")
    rr_ext.registry.register(
        ext.service_marketplace.files, service_id="files_marketplace"
    )
    rr_ext.registry.register(
        ext.service_marketplace.draft_files, service_id="files_marketplace_draft"
    )

    # indexers
    idx_ext.registry.register(ext.service.indexer, indexer_id="records_packages")
    idx_ext.registry.register(
        ext.service_marketplace.indexer, indexer_id="marketplace_items"
    )


def create_packages_api_blueprint(app):
    """Create packages api blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.package_records_resource.as_blueprint()


def create_packages_files_api_blueprint(app):
    """Create packages api blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.package_record_files_resource.as_blueprint()


def create_draft_files_api_blueprint(app):
    """Create draft files blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.package_draft_files_resource.as_blueprint()


def create_parent_links_api_blueprint(app):
    """Create draft files blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.package_parent_record_links_resource.as_blueprint()


def create_search_records_api_blueprint(app):
    """Create packages/resources blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.search_resource.as_blueprint()


def create_packages_context_api_blueprint(app):
    """Create package context blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.packages_context_resource.as_blueprint()


def create_marketplace_api_blueprint(app):
    """Create Marketplace blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.marketplace_resource.as_blueprint()


def create_marketplace_files_api_blueprint(app):
    """Create marketplace files api blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.marketplace_files_resource.as_blueprint()


def create_marketplace_draft_files_api_blueprint(app):
    """Create marketplace draft files blueprint."""
    ext = app.extensions["geo-rdm-records"]
    return ext.marketplace_draft_files_resource.as_blueprint()
