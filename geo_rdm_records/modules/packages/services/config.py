# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Service configuration."""

from invenio_drafts_resources.services.records.config import is_record
from invenio_rdm_records.services import config as rdm_config
from invenio_rdm_records.services.config import (
    has_doi,
    is_draft,
    is_draft_and_has_review,
    is_iiif_compatible,
    is_record_and_has_doi,
)
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base.config import FromConfig
from invenio_records_resources.services.base.links import Link
from invenio_records_resources.services.files.links import FileLink
from invenio_records_resources.services.records.links import pagination_links

from geo_rdm_records.base.records.types import GEORecordTypes
from geo_rdm_records.base.services.config import BaseGEOServiceConfig
from geo_rdm_records.base.services.schemas import ParentSchema
from geo_rdm_records.customizations.records.api import GEODraft, GEORecord

from ..records.api import GEOPackageDraft, GEOPackageRecord
from .components.context import PackageContextComponent
from .components.relationship import PackageRelationshipComponent
from .components.resource_type import PackageResourceTypeComponent
from .components.resources import (
    PackageResourceAccessComponent,
    PackageResourceCommunityComponent,
    PackageResourceIntegrationComponent,
)
from .links import RecordLink
from .permissions import PackagesPermissionPolicy
from .request.service import has_blog_requests
from .schemas import GEOPackageRecordSchema


class GEOPackageRecordServiceConfig(BaseGEOServiceConfig):
    """GEO Package record draft service config."""

    # Configurations
    service_id = "records_package"

    # Record and draft classes
    record_type = GEORecordTypes.package

    record_cls = GEOPackageRecord
    draft_cls = GEOPackageDraft

    # Configuring the resources classes
    resource_cls = GEORecord
    resource_draft_cls = GEODraft

    # Schemas
    schema = GEOPackageRecordSchema
    schema_parent = ParentSchema

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_RDM_PACKAGE_PERMISSION_POLICY",
        default=PackagesPermissionPolicy,
        import_string=True,
    )

    # Service components
    components = [
        PackageRelationshipComponent,
        PackageResourceIntegrationComponent,
        PackageResourceAccessComponent,
        PackageResourceCommunityComponent,
        PackageResourceTypeComponent,
        PackageContextComponent,
    ] + rdm_config.RDMRecordServiceConfig.components

    # Links
    links_item = {
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/packages/{id}"),
            else_=RecordLink("{+api}/packages/{id}/draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/packages/{id}"),
            else_=RecordLink("{+ui}/uploads/packages/{id}"),
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
        # IIIF
        "self_iiif_manifest": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/iiif/package:{id}/manifest"),
            else_=RecordLink("{+api}/iiif/package-draft:{id}/manifest"),
        ),
        "self_iiif_sequence": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/iiif/package:{id}/sequence/default"),
            else_=RecordLink("{+api}/iiif/package-draft:{id}/sequence/default"),
        ),
        # Files
        "files": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/packages/{id}/files"),
            else_=RecordLink("{+api}/packages/{id}/draft/files"),
        ),
        "files_import": RecordLink(
            "{+api}/packages/{id}/draft/actions/files-import", when=is_draft
        ),
        "latest": RecordLink("{+api}/packages/{id}/versions/latest", when=is_record),
        "latest_html": RecordLink("{+ui}/packages/{id}/latest", when=is_record),
        "draft": RecordLink("{+api}/packages/{id}/draft", when=is_record),
        "record": RecordLink("{+api}/packages/{id}", when=is_draft),
        # TODO: record_html temporarily needed for DOI registration, until
        # problems with self_doi has been fixed
        "record_html": RecordLink("{+ui}/packages/{id}", when=is_draft),
        "publish": RecordLink(
            "{+api}/packages/{id}/draft/actions/publish", when=is_draft
        ),
        "review": RecordLink("{+api}/packages/{id}/draft/review", when=is_draft),
        "submit-review": RecordLink(
            "{+api}/packages/{id}/draft/actions/submit-review",
            when=is_draft_and_has_review,
        ),
        "versions": RecordLink("{+api}/packages/{id}/versions"),
        "access_links": RecordLink("{+api}/packages/{id}/access/links"),
        # TODO: only include link when DOI support is enabled.
        "reserve_doi": RecordLink("{+api}/packages/{id}/draft/pids/doi"),
        # Package specialized links
        "context_html": RecordLink("{+ui}/packages/{id}/dashboard"),
        "context_resources": RecordLink(
            "{+api}/packages/context/{parent_id}/resources"
        ),
        "context_associate": RecordLink(
            "{+api}/packages/{id}/context/actions/associate"
        ),
        "context_dissociate": RecordLink(
            "{+api}/packages/{id}/context/actions/dissociate"
        ),
        "resources": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/packages/{id}/resources"),
            else_=RecordLink("{+api}/packages/{id}/draft/resources"),
        ),
        "resources_import": RecordLink(
            "{+api}/packages/{id}/draft/actions/resources-import", when=is_draft
        ),
        "blog": RecordLink("{+api}/packages/{id}/blog", when=is_record),
        "blog-submit": RecordLink(
            "{+api}/packages/{id}/actions/submit-blog",
            when=has_blog_requests,
        ),
    }

    links_search_community_records = pagination_links(
        "{+api}/communities/{id}/packages{?args*}"
    )


class GEOPackageFileRecordServiceConfig(rdm_config.RDMFileRecordServiceConfig):
    """Configuration for package files."""

    # Configurations
    service_id = "files_package"

    # Record class
    record_cls = GEOPackageRecord

    # Permission policy
    permission_policy_cls = FromConfig(
        "GEO_RDM_PACKAGE_PERMISSION_POLICY",
        default=PackagesPermissionPolicy,
        import_string=True,
    )

    file_links_item = {
        "self": FileLink("{+api}/packages/{id}/files/{key}"),
        "content": FileLink("{+api}/packages/{id}/files/{key}/content"),
        # FIXME: filename instead
        "iiif_canvas": FileLink(
            "{+api}/iiif/record:{id}/canvas/{key}", when=is_iiif_compatible
        ),
        "iiif_base": FileLink("{+api}/iiif/record:{id}:{key}", when=is_iiif_compatible),
        "iiif_info": FileLink(
            "{+api}/iiif/record:{id}:{key}/info.json", when=is_iiif_compatible
        ),
        "iiif_api": FileLink(
            "{+api}/iiif/record:{id}:{key}/{region=full}"
            "/{size=full}/{rotation=0}/{quality=default}.{format=png}",
            when=is_iiif_compatible,
        ),
    }


class GEOPackageDraftFileServiceConfig(rdm_config.RDMFileDraftServiceConfig):
    """Configuration for draft files."""

    # Configurations
    service_id = "files_package_draft"

    # Record class
    record_cls = GEOPackageDraft

    # Permission policy
    permission_action_prefix = "draft_"
    permission_policy_cls = FromConfig(
        "GEO_RDM_PACKAGE_PERMISSION_POLICY",
        default=PackagesPermissionPolicy,
        import_string=True,
    )

    file_links_list = {
        "self": RecordLink("{+api}/packages/{id}/draft/files"),
    }

    file_links_item = {
        "self": FileLink("{+api}/packages/{id}/draft/files/{key}"),
        "content": FileLink("{+api}/packages/{id}/draft/files/{key}/content"),
        "commit": FileLink("{+api}/packages/{id}/draft/files/{key}/commit"),
        # FIXME: filename instead
        "iiif_canvas": FileLink(
            "{+api}/iiif/draft:{id}/canvas/{key}", when=is_iiif_compatible
        ),
        "iiif_base": FileLink("{+api}/iiif/draft:{id}:{key}", when=is_iiif_compatible),
        "iiif_info": FileLink(
            "{+api}/iiif/draft:{id}:{key}/info.json", when=is_iiif_compatible
        ),
        "iiif_api": FileLink(
            "{+api}/iiif/draft:{id}:{key}/{region=full}"
            "/{size=full}/{rotation=0}/{quality=default}.{format=png}",
            when=is_iiif_compatible,
        ),
    }
