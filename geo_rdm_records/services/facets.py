# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Facets definitions."""

from flask_babelex import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet
from invenio_vocabularies.services.facets import VocabularyLabels

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
