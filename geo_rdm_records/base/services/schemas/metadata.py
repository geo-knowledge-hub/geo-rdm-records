# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Metadata schema definition."""

from flask_babelex import lazy_gettext as _
from invenio_rdm_records.services.schemas import MetadataSchema as BaseMetadataSchema
from invenio_rdm_records.services.schemas.metadata import (
    ContributorSchema as BaseContributorSchema,
)
from invenio_rdm_records.services.schemas.metadata import (
    CreatorSchema as BaseCreatorSchema,
)
from invenio_rdm_records.services.schemas.metadata import (
    PersonOrOrganizationSchema as BasePersonOrOrganizationSchema,
)
from invenio_rdm_records.services.schemas.metadata import (
    RelatedIdentifierSchema as BaseRelatedIdentifierSchema,
)
from invenio_rdm_records.services.schemas.metadata import VocabularySchema
from marshmallow import fields, validate
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode

from .location import FeatureSchema


class PersonOrOrganizationSchema(BasePersonOrOrganizationSchema):
    """Person or Organization schema."""

    email = SanitizedUnicode(required=False, validate=validate.Email())


class CreatorSchema(BaseCreatorSchema):
    """Creator schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)


class ContributorSchema(BaseContributorSchema):
    """Contributor schema."""

    person_or_org = fields.Nested(PersonOrOrganizationSchema, required=True)


class RelatedIdentifierSchema(BaseRelatedIdentifierSchema):
    """Related identifier schema."""

    title = SanitizedUnicode(required=False)

    description = SanitizedHTML(required=False)


class MetadataSchema(BaseMetadataSchema):
    """GEO Knowledge Hub Record Metadata field schema."""

    #
    # Base Metadata fields
    #
    creators = fields.List(
        fields.Nested(CreatorSchema),
        required=True,
        validate=validate.Length(min=1, error=_("Missing data for required field.")),
    )

    contributors = fields.List(fields.Nested(ContributorSchema))
    related_identifiers = fields.List(fields.Nested(RelatedIdentifierSchema))

    resource_type = fields.Nested(
        VocabularySchema,
        # In the GEO Knowledge Hub, the unique case where `resource type` is unavailable
        # is in the package record.
        dump_default={"id": "knowledge", "title": {"en": "Knowledge Package"}},
    )

    #
    # Locations
    #
    locations = fields.Nested(FeatureSchema)

    #
    # Target Audience
    #
    target_audiences = fields.List(fields.Nested(VocabularySchema))

    #
    # GEO Work Programme Activities
    #
    geo_work_programme_activity = fields.Nested(VocabularySchema)

    #
    # Engagement Priorities
    #
    engagement_priorities = fields.List(fields.Nested(VocabularySchema))
