# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test community integration of the Package API."""

from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)


def test_package_integration_with_communities(
    db, community_record, running_app, minimal_record
):
    """Basic smoke test for packages integration with communities."""
    draft = GEOPackageDraft.create(minimal_record)
    draft.commit()
    db.session.commit()

    package = GEOPackageRecord.publish(draft)
    package.commit()
    db.session.commit()

    package.parent.communities.add(community_record, default=True)
    package.parent.commit()
    package.commit()

    assert package.dumps()["parent"]["communities"] == {
        "default": str(community_record.id),
        "ids": [str(community_record.id)],
    }

    db.session.commit()
