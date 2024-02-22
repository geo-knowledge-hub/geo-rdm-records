# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records module configurations."""

from flask_babelex import lazy_gettext as _
from invenio_rdm_records.services import facets as rdm_facets

from geo_rdm_records.base.services import facets as geo_facets
from geo_rdm_records.modules.requests.community.config import CommunitySubmissionConfig
from geo_rdm_records.modules.security.permissions import views_permissions_factory

# UI Configurations
# ===================
GEO_RDM_PACKAGES_ROUTES = {
    "package-dashboard": "/packages/<pid_value>/dashboard",
    "package-dashboard-versions": "/packages/<pid_value>/dashboard/versions",
    "package-dashboard-resources": "/packages/<pid_value>/dashboard/resources",
    "package-dashboard-settings": "/packages/<pid_value>/dashboard/settings",
    "package-dashboard-members": "/packages/<pid_value>/dashboard/members",
}

GEO_RDM_PACKAGES_VERSION_SEARCH = {
    "facets": ["access_status", "resource_type", "language"],
    "sort": ["bestmatch", "newest", "oldest", "version"],
}
"""Search configuration to Search versions."""

GEO_RDM_PACKAGES_RESOURCES_SEARCH = {
    "facets": ["access_status", "resource_type", "language"],
    "sort": ["bestmatch", "newest", "oldest", "version"],
}
"""Search configuration to Search package resources."""

GEO_RDM_PACKAGES_VIEW_PERMISSIONS_FACTORY = views_permissions_factory
"""View permissions factory."""

# API Configurations
# ===================

#
# Resource
#

# Rest Resource
RDM_RECORD_RESOURCE = (
    "geo_rdm_records.modules.rdm.resources.resource.GEORDMRecordResource"
)

# Configuration
RDM_RECORD_RESOURCE_CFG = (
    "geo_rdm_records.modules.rdm.resources.config.GEORecordResourceConfig"
)

#
# Service
#

# Services
RDM_RECORD_SERVICE = "geo_rdm_records.modules.rdm.services.service.GEORDMRecordService"

RDM_REVIEW_SERVICE = "geo_rdm_records.modules.rdm.services.review.service.ReviewService"

RDM_IIIF_SERVICE = "geo_rdm_records.modules.iiif.service.IIIFService"

# Configuration
RDM_RECORD_SERVICE_CFG = (
    "geo_rdm_records.modules.rdm.services.config.GEORecordServiceConfig"
)

RDM_FILE_SERVICE_CFG = (
    "geo_rdm_records.modules.rdm.services.config.GEOFileRecordServiceConfig"
)

RDM_FILE_DRAFT_SERVICE_CFG = (
    "geo_rdm_records.modules.rdm.services.config.GEOFileDraftServiceConfig"
)

# Permissions
GEO_RDM_RECORDS_PERMISSION_POLICY = (
    "geo_rdm_records.base.services.permissions.BaseGEOPermissionPolicy"
)

GEO_RDM_PACKAGE_PERMISSION_POLICY = (
    "geo_rdm_records.modules.packages.services.permissions.PackagesPermissionPolicy"
)

#
# Search configuration
#
RDM_FACETS = {
    "base_type": {
        "facet": geo_facets.base_type,
        "ui": {
            "field": "resource_type.basetype",
        },
    },
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

RDM_SEARCH_PACKAGE_RESOURCE = {
    "facets": ["access_status", "resource_type", "base_type"],
    "sort": ["bestmatch", "newest", "oldest", "version"],
}

RDM_SEARCH_PACKAGE_RESOURCE_DRAFTS = {
    "facets": ["access_status", "is_published", "resource_type", "base_type"],
    "sort": ["bestmatch", "updated-desc", "updated-asc", "newest", "oldest", "version"],
}

#
# Review
#
RDM_COMMUNITY_SUBMISSION_OVERRIDE_CONFIG = CommunitySubmissionConfig

#
# Requests
#

# Default receiver
GEO_RDM_RECORDS_REQUESTS_DEFAULT_RECEIVER = None

#
# Notification configuration
#

# E-mail configuration
GEO_RDM_NOTIFICATION_DEFAULT_RECEIVER_EMAILS = []

#
# Checker configuration
#
GEO_RDM_CHECKER_LINKS_RETRY_CONFIG = {"retries": 5, "backoff_factor": 0.3}
"""Retry configurations (based on retry-requests library)."""

GEO_RDM_CHECKER_LINKS_REQUEST_CONFIG = {"timeout": 10}
"""Request configuration (based on requests (get method) library."""

GEO_RDM_CHECKER_LINKS_REPORT_TITLE = _(
    "GEO Knowledge Hub - Links status from your records"
)
"""Links status report title."""

GEO_RDM_CHECKER_OUTDATED_REPORT_TITLE = _("GEO Knowledge Hub - Your records status")
"""Outdated records report title."""

GEO_RDM_CHECKER_OUTDATED_CRITERIA = 6 * 365 / 12
"""Criteria used to set if a record is outdated."""


# OAI-PMH
# =======
# See https://github.com/inveniosoftware/invenio-oaiserver/blob/master/invenio_oaiserver/config.py

OAISERVER_RECORD_CLS = "geo_rdm_records.modules.rdm.records.api:GEORecord"
"""Record retrieval class (With support for both Packages and Records)."""

OAISERVER_RECORD_INDEX = ("geordmrecords-records", "geordmpackages-records")
"""Specify an Elastic index with records that should be exposed via OAI-PMH (Packages and Records)."""
