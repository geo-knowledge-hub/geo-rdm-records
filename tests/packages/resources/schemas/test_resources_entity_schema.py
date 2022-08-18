# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test relationship schema."""

from contextlib import nullcontext as does_not_raise

import pytest
from marshmallow import ValidationError

from geo_rdm_records.modules.packages.services.schemas.resources import (
    ResourceEntitySchema,
    ResourcesSchema,
)


#
# Local fixtures
#
@pytest.fixture
def basic_resource_entity(request):
    return dict(type=request.param, id="abcd-1234")


@pytest.mark.parametrize(
    "basic_resource_entity,expectation",
    [
        ("managed", does_not_raise()),
        ("related", does_not_raise()),
        ("test", pytest.raises(ValidationError)),
    ],
    indirect=["basic_resource_entity"],
)
def test_resource_entity_schema(basic_resource_entity, expectation):
    """Test the Relationship schema load operation."""
    with expectation:
        assert basic_resource_entity == ResourceEntitySchema().load(
            basic_resource_entity
        )
        assert basic_resource_entity == ResourceEntitySchema().dump(
            basic_resource_entity
        )


@pytest.mark.parametrize(
    "basic_resource_entity,expectation",
    [
        ("managed", does_not_raise()),
        ("related", does_not_raise()),
        ("test", pytest.raises(ValidationError)),
    ],
    indirect=["basic_resource_entity"],
)
def test_resource_schema(basic_resource_entity, expectation):
    """Test the load/dump operations of the Resource schema."""
    resource = dict(resources=[basic_resource_entity])

    with expectation:
        assert resource == ResourcesSchema().load(resource)
        assert resource == ResourcesSchema().dump(resource)
