# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services configuration."""

from invenio_drafts_resources.services.records.config import SearchOptions
from invenio_rdm_records.services import config as rdm_config
from invenio_rdm_records.services.customizations import FromConfigSearchOptions

from geo_rdm_records.records.api import GEODraft, GEORecord
from geo_rdm_records.services.params.facets import FacetsParam
from geo_rdm_records.services.params.search import LocationParam
from geo_rdm_records.services.schemas import GEORecordSchema


class GEOSearchOptionsMixin:
    """Customization of search options."""

    # search for the `FacetsParam` class to avoid error in future
    # changes on `SearchOptions.params_interpreters_cls`.
    params_interpreters_cls = list(
        map(
            lambda x: FacetsParam
            if getattr(x, "__name__", None) and x.__name__ == "FacetsParam"
            else x,
            [*SearchOptions.params_interpreters_cls, LocationParam.factory('metadata.locations.features.geometry')],
        )
    )


class GEOSearchOptions(GEOSearchOptionsMixin, rdm_config.RDMSearchOptions):
    """Search options for record search."""


class GEOSearchDraftsOptions(GEOSearchOptionsMixin, rdm_config.RDMSearchDraftsOptions):
    """Search options for record search."""


class GEOSearchVersionsOptions(
    GEOSearchOptionsMixin, rdm_config.RDMSearchVersionsOptions
):
    """Search options for record versioning search."""


class GEORecordServiceConfig(rdm_config.RDMRecordServiceConfig):
    """GEO record draft service config."""

    # Reord and draft classes
    record_cls = GEORecord
    draft_cls = GEODraft

    # Schemas
    schema = GEORecordSchema

    # Search configuration
    search = FromConfigSearchOptions("RDM_SEARCH", search_option_cls=GEOSearchOptions)
    search_drafts = FromConfigSearchOptions(
        "RDM_SEARCH_DRAFTS", search_option_cls=GEOSearchDraftsOptions
    )
    search_versions = FromConfigSearchOptions(
        "RDM_SEARCH_VERSIONING", search_option_cls=GEOSearchVersionsOptions
    )


class GEOFileRecordServiceConfig(rdm_config.RDMFileRecordServiceConfig):
    """Configuration for record files."""

    record_cls = GEORecord


class GEOFileDraftServiceConfig(rdm_config.RDMFileDraftServiceConfig):
    """Configuration for draft files."""

    record_cls = GEODraft
