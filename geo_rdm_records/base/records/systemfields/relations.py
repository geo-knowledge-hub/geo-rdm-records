# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Custom relations."""

from invenio_records.dictutils import dict_lookup, dict_set
from invenio_records.systemfields.relations.relations import ListRelation
from invenio_records.systemfields.relations.results import (
    RelationListResult as BaseRelationListResult,
)
from invenio_records_resources.records.systemfields import PIDRelation


#
# Award result
#
class AwardRelationListResult(BaseRelationListResult):
    """Custom Award Relation List result."""

    def _dereference_one(self, data, keys, attrs):
        """Dereference a single object into a dict."""
        # Get related record
        obj = self.resolve(data[self.field._value_key_suffix])
        # Inject selected key/values from related record into
        # the current record.

        # From record dictionary
        if keys is None:
            data.update({k: v for k, v in obj.items()})
        else:
            new_obj = {}

            # Custom class created to support extra `keys` in the
            # Award object. This is used to include `icon` and `disclaimer` properties.
            for k in keys:
                try:
                    val = dict_lookup(obj, k)
                    if val:
                        dict_set(new_obj, k, val)
                except KeyError:
                    pass
            data.update(new_obj)

        # From record attributes (i.e. system fields)
        for a in attrs:
            data[a] = getattr(obj, a)

        return data

    def clean(self, keys=None, attrs=None):
        """Clean the dereferenced attributes inside the record.

        Reverses changes made by dereference.
        """
        return self._apply_items(self._dereference_one, keys, attrs)


#
# Award List Relation
#
class FundingAwardListRelation(ListRelation):
    """List Relation for custom Funding Award."""

    result_cls = AwardRelationListResult


class AwardRelation(FundingAwardListRelation, PIDRelation):
    """Custom Award Relation."""
