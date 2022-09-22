# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Search services."""

from invenio_drafts_resources.services.records.config import is_draft, is_record
from invenio_rdm_records.services.config import (
    has_doi,
    is_draft_and_has_review,
    is_record_and_has_doi,
)
from invenio_rdm_records.services.customizations import FromConfig
from invenio_records_resources.services import ConditionalLink, pagination_links
from invenio_records_resources.services.base.links import Link
from invenio_records_resources.services.records.links import RecordLink

from geo_rdm_records.base.services.config import BaseGEOServiceConfig
from geo_rdm_records.base.services.permissions import BaseGEOPermissionPolicy
from geo_rdm_records.base.services.schemas import ParentSchema
from geo_rdm_records.customizations.records.api import GEODraft, GEORecord
from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)

from .links import LinksRegistryType
from .results import MutableRecordList, ResultRegistryType
from .schemas import GEORecordSchema


class SearchRecordServiceConfig(BaseGEOServiceConfig):
    """Service factory configuration."""

    # Common configuration
    service_id = "records_search"

    # Indices used to do the search
    indices = [
        GEORecord.index.search_alias,
        GEOPackageRecord.index.search_alias,
    ]

    indices_draft = [GEODraft.index.search_alias, GEOPackageDraft.index.search_alias]

    # Schemas
    schema = GEORecordSchema
    schema_parent = ParentSchema

    # Result classes
    result_list_cls = MutableRecordList
    results_registry_type = ResultRegistryType

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_RDM_PACKAGE_PERMISSION_POLICY",
        default=BaseGEOPermissionPolicy,
        import_string=True,
    )

    # Links
    links_registry_type = LinksRegistryType

    links_item = {
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/{entity}/{id}"),
            else_=RecordLink("{+api}/{entity}/{id}/draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/{entity}/{id}"),
            else_=RecordLink("{+ui}/uploads/{entity}/{id}"),
        ),
        "self_doi": Link(
            "{+ui}/doi/{+pid_doi}",
            when=is_record_and_has_doi,
            vars=lambda record, vars: vars.update(
                {
                    f"pid_{scheme}": pid["identifier"]
                    for (scheme, pid) in record.pids.items()
                }
            ),
        ),
        "doi": Link(
            "https://doi.org/{+pid_doi}",
            when=has_doi,
            vars=lambda record, vars: vars.update(
                {
                    f"pid_{scheme}": pid["identifier"]
                    for (scheme, pid) in record.pids.items()
                }
            ),
        ),
        "self_iiif_manifest": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/iiif/record:{id}/manifest"),
            else_=RecordLink("{+api}/iiif/draft:{id}/manifest"),
        ),
        "self_iiif_sequence": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/iiif/record:{id}/sequence/default"),
            else_=RecordLink("{+api}/iiif/draft:{id}/sequence/default"),
        ),
        "files": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/{entity}/{id}/files"),
            else_=RecordLink("{+api}/{entity}/{id}/draft/files"),
        ),
        "latest": RecordLink("{+api}/{entity}/{id}/versions/latest", when=is_record),
        "latest_html": RecordLink("{+ui}/{entity}/{id}/latest", when=is_record),
        "draft": RecordLink("{+api}/{entity}/{id}/draft", when=is_record),
        "record": RecordLink("{+api}/{entity}/{id}", when=is_draft),
        # TODO:
        #  Note from Invenio RDM Records: record_html temporarily needed for DOI registration, until
        #                                 problems with self_doi has been fixed
        "record_html": RecordLink("{+ui}/{entity}/{id}", when=is_draft),
        "publish": RecordLink(
            "{+api}/{entity}/{id}/draft/actions/publish", when=is_draft
        ),
        "review": RecordLink("{+api}/{entity}/{id}/draft/review", when=is_draft),
        "submit-review": RecordLink(
            "{+api}/{entity}/{id}/draft/actions/submit-review",
            when=is_draft_and_has_review,
        ),
        "versions": RecordLink("{+api}/{entity}/{id}/versions"),
        "access_links": RecordLink("{+api}/{entity}/{id}/access/links"),
        # TODO:
        #  Note from Invenio RDM Records: only include link when DOI support is enabled.
        "reserve_doi": RecordLink("{+api}/{entity}/{id}/draft/pids/doi"),
    }

    links_search = pagination_links("{+api}/search{?args*}")

    links_search_community_records = pagination_links(
        "{+api}/communities/{id}/search{?args*}"
    )
