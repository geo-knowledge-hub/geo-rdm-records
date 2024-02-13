# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Package Record JSONSchemas."""

import pytest
from jsonschema.exceptions import ValidationError

from geo_rdm_records.modules.rdm.records.api import GEORecord as Record


#
# Assertion helpers
#
def validates(data):
    """Assertion function used to validate according to the schema."""
    data["$schema"] = "local://records/geordmrecords-records-record-v1.0.0.json"
    Record(data).validate()
    return True


def validates_meta(data):
    """Validate metadata fields."""
    return validates({"metadata": data})


def fails(data):
    """Assert that validation fails."""
    pytest.raises(ValidationError, validates, data)
    return True


def fails_meta(data):
    """Assert that validation fails for metadata."""
    pytest.raises(ValidationError, validates_meta, data)
    return True


#
# Tests metadata
#
def test_geo_work_programme_activity_schema(appctx):
    """Test the GEO Work programme activity field schema."""
    assert validates_meta({"geo_work_programme_activity": {"id": "geo-vener"}})
    assert fails_meta({"geo_work_programme_activity": {"id": 777}})


def test_engagement_priority_schema(appctx):
    """Test the Engagement Priorities field schema."""
    assert validates_meta({"engagement_priorities": [{"id": "sdg-goal-01"}]})
    assert fails_meta({"engagement_priorities": [{"id": 777}]})


def test_target_audiences_schema(appctx):
    """Test the Target Audiences field schema."""
    assert validates_meta({"target_audiences": [{"id": "geo-scientist"}]})
    assert fails_meta({"target_audiences": [{"id": 777}]})
