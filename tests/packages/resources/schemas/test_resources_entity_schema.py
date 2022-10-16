# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test relationship schema."""

import pytest

from geo_rdm_records.modules.packages.services.schemas.resources import (
    ResourceEntitySchema,
    ResourcesSchema,
)


#
# Local fixtures
#
@pytest.fixture
def basic_resource_entity():
    return dict(id="abcd-1234")


def test_resource_entity_schema(basic_resource_entity):
    """Test the Relationship schema load operation."""
    assert basic_resource_entity == ResourceEntitySchema().load(basic_resource_entity)
    assert basic_resource_entity == ResourceEntitySchema().dump(basic_resource_entity)


def test_resource_schema(basic_resource_entity):
    """Test the load/dump operations of the Resource schema."""
    resource = dict(resources=[basic_resource_entity])

    assert resource == ResourcesSchema().load(resource)
    assert resource == ResourcesSchema().dump(resource)
