# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Services configuration."""

from invenio_drafts_resources.services.records.config import SearchOptions
from invenio_rdm_records.services import config as rdm_config
from invenio_records_resources.services.base.config import FromConfigSearchOptions

from .params import BoundingBoxParam, FacetsParam


class GEOSearchOptionsMixin:
    """Customization of search options."""

    # search for the `FacetsParam` class to avoid error in future
    # changes on `SearchOptions.params_interpreters_cls`.
    params_interpreters_cls = list(
        map(
            lambda x: (
                FacetsParam  # replacing the `FacetsParams` by the custom one.
                if getattr(x, "__name__", None) and x.__name__ == "FacetsParam"
                else x
            ),
            [
                *SearchOptions.params_interpreters_cls,
                BoundingBoxParam.factory("metadata.locations.features.geometry"),
            ],
        )
    )


class GEOSearchOptions(GEOSearchOptionsMixin, rdm_config.RDMSearchOptions):
    """Search options for record search."""

    params_interpreters_cls = rdm_config.RDMSearchOptions.params_interpreters_cls + [
        BoundingBoxParam.factory("metadata.locations.features.geometry")
    ]


class GEOSearchDraftsOptions(GEOSearchOptionsMixin, rdm_config.RDMSearchDraftsOptions):
    """Search options for record search."""

    params_interpreters_cls = (
        rdm_config.RDMSearchDraftsOptions.params_interpreters_cls
        + [BoundingBoxParam.factory("metadata.locations.features.geometry")]
    )


class GEOSearchVersionsOptions(
    GEOSearchOptionsMixin, rdm_config.RDMSearchVersionsOptions
):
    """Search options for record versioning search."""

    params_interpreters_cls = (
        rdm_config.RDMSearchVersionsOptions.params_interpreters_cls
        + [BoundingBoxParam.factory("metadata.locations.features.geometry")]
    )


class BaseGEOServiceConfig(rdm_config.RDMRecordServiceConfig):
    """GEO record draft service config."""

    # Search configuration
    search = FromConfigSearchOptions(
        "RDM_SEARCH",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=GEOSearchOptions,
    )
    search_drafts = FromConfigSearchOptions(
        "RDM_SEARCH_DRAFTS",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=GEOSearchDraftsOptions,
    )
    search_versions = FromConfigSearchOptions(
        "RDM_SEARCH_VERSIONING",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=GEOSearchVersionsOptions,
    )

    # Indices used to suggest related content
    indices_more_like_this = []

    # Fields used to suggest related content
    fields_more_like_this = [
        "parent.communities.ids",
        "metadata.title",
        "metadata.description",
        "metadata.subjects.subject",
        "metadata.subjects.subject.keyword",
        "metadata.subjects.subject.subject",
        "metadata.engagement_priorities.title",
        "metadata.additional_titles.title",
        "metadata.additional_descriptions.description",
        "metadata.related_identifiers.description",
        "metadata.resource_type.id",
        "metadata.target_audiences.id",
        "metadata.related_identifiers.title",
        "metadata.related_identifiers.description",
    ]
