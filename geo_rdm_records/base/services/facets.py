# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Facets definitions."""

from flask_babelex import gettext as _
from invenio_records_resources.services.records.facets import (
    NestedTermsFacet,
    TermsFacet,
)
from invenio_vocabularies.services.facets import VocabularyLabels

#
# Record category
#
record_category = TermsFacet(
    field="parent.category",
    label=_("Category"),
    value_labels={
        "open": "Open",
        "marketplace": "Commercial",
    },
)

#
# Record type
#
record_type = TermsFacet(
    field="parent.type",
    label=_("Record Type"),
    value_labels={
        "package": "Knowledge Package",
        "resource": "Knowledge Resource",
        "marketplace-item": "Marketplace Item",
    },
)

#
# GEO Work Programme Activities Facet
#
geo_work_programme_activity = TermsFacet(
    field="metadata.geo_work_programme_activity.id",
    label=_("GEO Work Programme Activities"),
    value_labels=VocabularyLabels("geowptypes"),
)

#
# Target Audience
#
target_audience = TermsFacet(
    field="metadata.target_audiences.id",
    label=_("Target Audience"),
    value_labels=VocabularyLabels("targetaudiencestypes"),
)

#
# Engagement Priorities Facet
#
engagement_priority = TermsFacet(
    field="metadata.engagement_priorities.id",
    label=_("Engagement Priorities"),
    value_labels=VocabularyLabels("engagementprioritiestypes"),
)

#
# Base Resource Type
#
base_type = TermsFacet(
    field="metadata.resource_type.props.basetype",
    label=_("Base resource type"),
    value_labels=VocabularyLabels("resourcetypes"),
)

#
# Resource type
#
resource_type = NestedTermsFacet(
    field="metadata.resource_type.props.type",
    subfield="metadata.resource_type.props.subtype",
    splitchar="::",
    label=_("Resource Type"),
    value_labels=VocabularyLabels("resourcetypes"),
)
