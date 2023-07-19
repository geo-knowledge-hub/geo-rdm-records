# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test relationship schema."""

import pytest

from geo_rdm_records.modules.packages.services.schemas import RelationshipSchema


#
# Local fixtures
#
@pytest.fixture()
def basic_relationship():
    return dict(
        resources=[
            {"id": "abcd-1234", "relation_type": "related"},
            {"id": "abcd-1234", "relation_type": "managed"},
        ],
    )


#
# Tests
#
def test_relationship_schema(basic_relationship):
    """Test the load/dump operations of the Relationship schema."""
    assert basic_relationship == RelationshipSchema().load(basic_relationship)
    assert basic_relationship == RelationshipSchema().dump(basic_relationship)
