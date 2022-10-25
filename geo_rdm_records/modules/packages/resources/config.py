# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource config for the Packages API."""

from copy import deepcopy

from flask_resources import ResponseHandler
from invenio_drafts_resources.resources import RecordResourceConfig
from invenio_rdm_records.resources import config as rdm_resources_config

from geo_rdm_records.base.resources import BaseGEOResourceConfig
from geo_rdm_records.base.resources.serializers import UIRecordJSONSerializer

#
# Response handlers
#
record_serializers = deepcopy(rdm_resources_config.record_serializers)
record_serializers.update(
    {"application/vnd.inveniordm.v1+json": ResponseHandler(UIRecordJSONSerializer())}
)


#
# Package Records and versions.
#
class GEOPackageRecordResourceConfig(BaseGEOResourceConfig):
    """Record resource configuration."""

    blueprint_name = "packages"
    url_prefix = "/packages"

    # Response handlers
    response_handlers = record_serializers

    # Packages API Routes
    routes = deepcopy(rdm_resources_config.RDMRecordResourceConfig.routes)

    # Packages endpoints
    routes["item-validate"] = "/<pid_value>/draft/actions/validate"
    routes["item-resources-import"] = "/<pid_value>/draft/actions/resources-import"

    # Resources endpoints
    routes["item-resources"] = "/<pid_value>/resources"
    routes["item-draft-resources"] = "/<pid_value>/draft/resources"

    # Community endpoints
    routes["community-records"] = "/communities/<pid_value>/packages"


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


class GEOPackageParentRelationshipConfig(RecordResourceConfig):
    """Bibliographic package context resource configuration."""

    blueprint_name = "package_parent_relationship"
    url_prefix = "/packages/<pid_value>/context"

    # Response handlers
    response_handlers = record_serializers

    routes = {
        "context": "",
        "context-associate": "/actions/associate",
        "context-dissociate": "/actions/dissociate",
    }
