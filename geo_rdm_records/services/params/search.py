# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Search Params."""

from functools import partial

from invenio_records_resources.services.records.params.base import \
    ParamInterpreter


class LocationParam(ParamInterpreter):
    """Evaluates the 'location' parameter."""

    def __init__(self, field_name, config):
        """Construct."""
        self.field_name = field_name
        super().__init__(config)

    @classmethod
    def factory(cls, field):
        """Create a new filter parameter."""
        return partial(cls, field)

    def apply(self, identity, search, params):
        """Evaluate the allversions parameter on the search."""
        location = params.get('location')
        if location:
            # preparing the location object
            type_, args_ = location.split(':')

            if args_:
                # todo: handle possible errors.
                args_ = list(map(lambda x: float(x), args_.split(',') or []))
                assert len(args_) == 4

            if type_ == 'bbox':
                coordinates = [args_[0:2], args_[2:]]

                search = search.filter('geo_shape', **{
                    self.field_name: {
                        'shape': {
                            'type': 'envelope',
                            'coordinates': coordinates
                        },
                        'relation': 'intersects'
                    }
                })
        return search
