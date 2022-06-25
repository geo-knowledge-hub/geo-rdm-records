# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Records API."""

import invenio_rdm_records.records.models as rdm_models
from invenio_drafts_resources.records import Draft, Record
from invenio_rdm_records.records.api import CommonFieldsMixin as BaseCommonFieldsMixin
from invenio_rdm_records.records.systemfields import HasDraftCheckField
from invenio_records.systemfields import ConstantField, RelationsField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import (
    FilesField,
    IndexField,
    PIDListRelation,
    PIDNestedListRelation,
    PIDRelation,
)
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.records.api import Vocabulary


class CommonFieldsMixin(BaseCommonFieldsMixin):
    """Common system fields between records and drafts."""

    schema = ConstantField("$schema", "local://records/geo-record-v4.0.0.json")

    relations = RelationsField(
        #
        # Customized fields
        #
        target_audiences=PIDListRelation(
            "metadata.target_audiences",
            attrs=["id", "title", "props.type"],
            pid_field=Vocabulary.pid.with_type_ctx("targetaudiencestypes"),
            cache_key="target_audiences",
        ),
        geo_work_programme_activity=PIDRelation(
            "metadata.geo_work_programme_activity",
            attrs=["id", "title", "props.type"],
            pid_field=Vocabulary.pid.with_type_ctx("geowptypes"),
            cache_key="geo_work_programme_activity",
        ),
        engagement_priorities=PIDListRelation(
            "metadata.engagement_priorities",
            attrs=["id", "title", "props.type", "props.subtype"],
            pid_field=Vocabulary.pid.with_type_ctx("engagementprioritiestypes"),
            cache_key="engagement_priorities",
        ),

        #
        # InvenioRDM DataCite Relations
        #
        creator_affiliations=PIDNestedListRelation(
            "metadata.creators",
            relation_field="affiliations",
            keys=["name"],
            pid_field=Affiliation.pid,
            cache_key="affiliations",
        ),
        contributor_affiliations=PIDNestedListRelation(
            "metadata.contributors",
            relation_field="affiliations",
            keys=["name"],
            pid_field=Affiliation.pid,
            cache_key="affiliations",
        ),
        funding_funder=PIDListRelation(
            "metadata.funding",
            relation_field="funder",
            keys=["name"],
            pid_field=Funder.pid,
            cache_key="funders",
        ),
        funding_award=PIDListRelation(
            "metadata.funding",
            relation_field="award",
            keys=["title", "number", "identifiers"],
            pid_field=Award.pid,
            cache_key="awards",
        ),
        languages=PIDListRelation(
            "metadata.languages",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
            cache_key="languages",
        ),
        resource_type=PIDRelation(
            "metadata.resource_type",
            keys=["title", "props.type", "props.subtype"],
            pid_field=Vocabulary.pid.with_type_ctx("resourcetypes"),
            cache_key="resource_type",
            value_check=dict(tags=["depositable"]),
        ),
        subjects=PIDListRelation(
            "metadata.subjects",
            keys=["subject", "scheme"],
            pid_field=Subject.pid,
            cache_key="subjects",
        ),
        licenses=PIDListRelation(
            "metadata.rights",
            keys=["title", "description", "icon", "props.url", "props.scheme"],
            pid_field=Vocabulary.pid.with_type_ctx("licenses"),
            cache_key="licenses",
        ),
        related_identifiers=PIDListRelation(
            "metadata.related_identifiers",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("resourcetypes"),
            cache_key="resource_type",
            relation_field="resource_type",
            value_check=dict(tags=["linkable"]),
        ),
        title_types=PIDListRelation(
            "metadata.additional_titles",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("titletypes"),
            cache_key="title_type",
            relation_field="type",
        ),
        title_languages=PIDListRelation(
            "metadata.additional_titles",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
            cache_key="languages",
            relation_field="lang",
        ),
        creators_role=PIDListRelation(
            "metadata.creators",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("creatorsroles"),
            cache_key="role",
            relation_field="role",
        ),
        contributors_role=PIDListRelation(
            "metadata.contributors",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributorsroles"),
            cache_key="role",
            relation_field="role",
        ),
        description_type=PIDListRelation(
            "metadata.additional_descriptions",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("descriptiontypes"),
            cache_key="description_type",
            relation_field="type",
        ),
        description_languages=PIDListRelation(
            "metadata.additional_descriptions",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
            cache_key="languages",
            relation_field="lang",
        ),
        date_types=PIDListRelation(
            "metadata.dates",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("datetypes"),
            cache_key="date_types",
            relation_field="type",
        ),
        relation_types=PIDListRelation(
            "metadata.related_identifiers",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("relationtypes"),
            cache_key="relation_types",
            relation_field="relation_type",
        ),
    )


#
# Draft API
#
class GEOFileDraft(FileRecord):
    """Record (Draft) File abstraction class."""

    model_cls = rdm_models.RDMFileDraftMetadata
    records_cls = None


class GEODraft(CommonFieldsMixin, Draft):
    """Record (Draft) Metadata manipulation class API."""

    model_cls = rdm_models.RDMDraftMetadata

    index = IndexField(
        "geordmrecords-drafts-draft-v5.0.0", search_alias="geordmrecords"
    )

    files = FilesField(
        store=False,
        file_cls=GEOFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()


#
# Record API
#
class GEOFileRecord(FileRecord):
    """Record File abstraction class."""

    model_cls = rdm_models.RDMFileRecordMetadata
    records_cls = None


class GEORecord(CommonFieldsMixin, Record):
    """Record Metadata manipulation class API."""

    model_cls = rdm_models.RDMRecordMetadata

    index = IndexField(
        "geordmrecords-records-record-v5.0.0", search_alias="geordmrecords-records"
    )

    files = FilesField(
        store=False,
        file_cls=GEOFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField(GEODraft)


GEOFileDraft.record_cls = GEODraft
GEOFileRecord.record_cls = GEORecord
