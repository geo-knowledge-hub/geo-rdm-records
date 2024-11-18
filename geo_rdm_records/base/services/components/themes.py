# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Service constraints."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service as vocabulary_service
from pydash import py_


def get_programme_themes(identity, programme_id):
    """Get GEO Themes associated with a given GEO Work Programme Activity.

    Args:
        identity (flask_principal.Identity): User identity.

        programme_id (str): GEO Work Programme Activity ID.

    Returns:
        list: List with the GEO Themes associated to the GEO Work Programme Activity.
    """
    programme_id = ("geowptypes", programme_id)
    programme_themes = []

    try:
        programme_data = vocabulary_service.read(identity=identity, id_=programme_id)

        programme_data = programme_data.to_dict()

        programme_themes = py_.get(programme_data, "tags", [])
        programme_themes = py_.map(programme_themes, lambda x: dict(id=x))

    except BaseException:  # noqa
        # If not possible to get the themes, return nothing.
        pass

    return programme_themes


class GEOThemeComponent(ServiceComponent):
    """Service component for the ``GEO Theme`` field."""

    _field_name = "geo_work_programme_activity"

    def _get_gwp(self, record):
        """Get GWP from a record."""
        gwp_object = record.metadata.get("geo_work_programme_activity", {})

        return gwp_object.get("id")

    def _has_gwp(self, record):
        """Check if a given record has any GWP associated."""
        gwp = self._get_gwp(record)

        return gwp is not None

    def _include_themes(self, record, themes):
        """Include themes in a given record."""
        # Extract and merge engagements with themes.
        engagements = record.metadata.get("engagement_priorities", [])
        engagements.extend(themes)

        # Remove duplicates and save the result in the record
        record.metadata["engagement_priorities"] = py_.uniq_by(engagements, "id")

    def _mutate_record(self, identity, record):
        """Mutate record with GEO Themes."""
        if self._has_gwp(record):
            # get programme
            programme = self._get_gwp(record)

            # extract themes and merge them
            themes = get_programme_themes(identity, programme)

            self._include_themes(record, themes)

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        self._mutate_record(identity, record)

    def update_draft(self, identity, data=None, record=None, errors=None, **kwargs):
        """Update draft handler."""
        self._mutate_record(identity, record)

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft relationship."""
        self._mutate_record(identity, record)
