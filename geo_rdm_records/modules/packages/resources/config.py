# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource config for the Packages API."""

from invenio_rdm_records.resources import config as rdm_resources_config


#
# Package Records and versions.
#
class GEOPackageRecordResourceConfig(rdm_resources_config.RDMRecordResourceConfig):
    """Record resource configuration."""

    blueprint_name = "packages"
    url_prefix = "/packages"

    routes = {
        **rdm_resources_config.RDMRecordResourceConfig.routes,
        "item-resources": "/<pid_value>/resources",
        "item-draft-resources": "/<pid_value>/draft/resources",
    }


#
# Record files
#
class GEOPackageRecordFilesResourceConfig(
    rdm_resources_config.RDMRecordFilesResourceConfig
):
    """Bibliographic record files resource config."""

    allow_upload = False

    blueprint_name = "package_files"
    url_prefix = "/packages/<pid_value>"


#
# Draft files
#
class GEOPackageDraftFilesResourceConfig(
    rdm_resources_config.RDMDraftFilesResourceConfig
):
    """Bibliographic record (draft mode) files resource config."""

    blueprint_name = "package_draft_files"
    url_prefix = "/packages/<pid_value>/draft"


#
# Parent record links
#
class GEOPackageParentRecordLinksResourceConfig(
    rdm_resources_config.RDMParentRecordLinksResourceConfig
):
    """Bibliographic parent record resource configuration."""

    blueprint_name = "package_parent"
    url_prefix = "/packages/<pid_value>/access"
