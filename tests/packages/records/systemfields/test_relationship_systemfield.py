# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test relationship system field."""

from geo_rdm_records.customizations.records.api import GEODraft
from geo_rdm_records.modules.packages.records.systemfields.relationship import (
    PackageRelationship,
)


def test_package_relationship_creation(running_app, minimal_record):
    """Test the ``creation`` method from the Relationship entity class."""

    # 1. Creating the records
    record_1 = GEODraft.create(minimal_record)
    record_1.commit()

    record_2 = GEODraft.create(minimal_record)
    record_2.commit()

    # 2. Creating the relationship data
    managed_resources = PackageRelationship.linked_resources_cls(
        [{"id": record_1.pid.pid_value}]
    )
    related_resources = PackageRelationship.linked_resources_cls(
        [{"id": record_2.pid.pid_value}]
    )

    # 3. Testing the entity initializer
    relationship_entity_obj = PackageRelationship(
        managed_resources=managed_resources, related_resources=related_resources
    )

    assert len(relationship_entity_obj.managed_resources) == 1
    assert len(relationship_entity_obj.related_resources) == 1
    assert relationship_entity_obj.dump() == dict(
        managed_resources=[{"id": record_1.pid.pid_value}],
        related_resources=[{"id": record_2.pid.pid_value}],
    )


def test_package_relationship_from_dict(running_app):
    """Test the ``from_dict`` method from the Relationship entity class."""

    # 1. Creating the relationship base class
    relationship_dict = dict(
        managed_resources=[{"id": "abcd-123"}],
        related_resources=[{"id": "efgh-456"}],
    )

    # 2. Testing the ``from_dict`` method.
    relationship_entity_obj = PackageRelationship.from_dict(relationship_dict)

    assert len(relationship_entity_obj.managed_resources) == 1
    assert len(relationship_entity_obj.related_resources) == 1
    assert relationship_entity_obj.dump() == relationship_dict

    # 3. Refreshing the relationship content using a dict
    relationship_dict_2 = relationship_dict.copy()
    relationship_managed = [{"id": "abcd-123"}, {"id": "abcd-321"}, {"id": "abcd-132"}]

    relationship_dict_2.update(dict(managed_resources=relationship_managed))
    relationship_entity_obj.refresh_from_dict(relationship_dict_2)

    assert len(relationship_entity_obj.managed_resources) == 3
    assert len(relationship_entity_obj.related_resources) == 1
    assert relationship_entity_obj.dump() == dict(
        related_resources=relationship_dict["related_resources"],
        managed_resources=relationship_managed,
    )
