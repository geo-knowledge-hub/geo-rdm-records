# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test relationship schema."""

import pytest

from geo_rdm_records.modules.rdm.services.schemas import ParentRelationshipSchema


#
# Local fixtures
#
@pytest.fixture()
def basic_relationship():
    return dict(managed_by={"id": "abcd-1234"})


#
# Tests
#
def test_relationship_schema(basic_relationship):
    """Test the load/dump operations of the Relationship schema."""
    assert basic_relationship == ParentRelationshipSchema().load(basic_relationship)
    assert basic_relationship == ParentRelationshipSchema().dump(basic_relationship)
