# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records module configurations."""

from invenio_rdm_records.services import facets as rdm_facets

from geo_rdm_records.modules.resources.services import facets as geo_facets

#
# Resource
#

# Rest Resource
RDM_RECORD_RESOURCE = (
    "geo_rdm_records.modules.resources.resources.resource.GEORDMRecordResource"
)

# Configuration
RDM_RECORD_RESOURCE_CFG = (
    "geo_rdm_records.modules.resources.resources.config.GEORecordResourceConfig"
)

#
# Service
#

# Services
RDM_RECORD_SERVICE = (
    "geo_rdm_records.modules.resources.services.service.GEORDMRecordService"
)

# Configuration
RDM_RECORD_SERVICE_CFG = (
    "geo_rdm_records.modules.resources.services.config.GEORecordServiceConfig"
)

RDM_FILE_SERVICE_CFG = (
    "geo_rdm_records.modules.resources.services.config.GEOFileRecordServiceConfig"
)

RDM_FILE_DRAFT_SERVICE_CFG = (
    "geo_rdm_records.modules.resources.services.config.GEOFileDraftServiceConfig"
)

#
# Search configuration
#
RDM_FACETS = {
    "access_status": {
        "facet": rdm_facets.access_status,
        "ui": {
            "field": "access.status",
        },
    },
    "is_published": {
        "facet": rdm_facets.is_published,
        "ui": {
            "field": "is_published",
        },
    },
    "language": {
        "facet": rdm_facets.language,
        "ui": {
            "field": "languages",
        },
    },
    "resource_type": {
        "facet": rdm_facets.resource_type,
        "ui": {
            "field": "resource_type.type",
            "childAgg": {
                "field": "resource_type.subtype",
            },
        },
    },
    "subject": {
        "facet": rdm_facets.subject,
        "ui": {
            "field": "subjects.subject",
        },
    },
    "subject_nested": {
        "facet": rdm_facets.subject_nested,
        "ui": {
            "field": "subjects.scheme",
            "childAgg": {
                "field": "subjects.subject",
            },
        },
    },
    "engagement_priority": {
        "facet": geo_facets.engagement_priority,
        "ui": {"field": "engagement_priorities.type"},
    },
    "target_audience": {
        "facet": geo_facets.target_audience,
        "ui": {"field": "target_audiences.type"},
    },
    "geo_work_programme_activity": {
        "facet": geo_facets.geo_work_programme_activity,
        "ui": {"field": "geo_work_programme_activity.type"},
    },
}
