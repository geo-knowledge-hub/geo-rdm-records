# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Search Params."""

from functools import partial

from geojson import Point
from invenio_records_resources.services.errors import QuerystringValidationError
from invenio_records_resources.services.records.params.base import ParamInterpreter


def _validate_point_coordinates(point):
    """Validate the coordinates from a point."""
    lon, lat = point.coordinates

    if not point.is_valid:
        raise QuerystringValidationError('Point used to created the bounding box is not valid', point.errors())

    # ToDo: Check 180th meridian cases
    if (lat < -90.0) or (lat > 90.0):
        raise QuerystringValidationError('latitude is out-of range [-90, 90]')

    if (lon < -180.0) or (lon > 180.0):
        raise QuerystringValidationError('longitude is out-of range [-180, 180]')


def validate_bounding_box(value):
    """Validate the bbox object.

    See:
        https://datatracker.ietf.org/doc/html/rfc7946#section-5
    """
    value = value.split(",")

    if len(value) != 4:
        raise QuerystringValidationError("A bounding box must be defined "
                                         "by 2 Point (TopLeft, BottomRight). "
                                         "This is represented by a array with "
                                         "four elements: [lon, lat, lon, lat]")

    # validating the bounding box points
    list(
        map(lambda x: _validate_point_coordinates(x), [
            Point(*value[0:2]), Point(*value[2:])
        ]))


class BoundingBoxParam(ParamInterpreter):
    """Evaluates the 'bbox' parameter."""

    def __init__(self, field_name, config):
        """Construct."""
        self.field_name = field_name
        super().__init__(config)

    @classmethod
    def factory(cls, field):
        """Create a new filter parameter."""
        return partial(cls, field)

    def apply(self, identity, search, params):
        """Evaluate the `bbox` parameter on the query string."""
        bbox = params.get('bbox')
        if bbox:
            # validating the `bbox` object
            bbox = bbox.split(',') or []

            validate_bounding_box(bbox)

            # creating the bbox search filter
            bbox = list(map(float, bbox))

            bbox = {
                "top_left": bbox[0:2],
                "bottom_right": bbox[2:]
            }

            search = search.filter("geo_bounding_box", **{
                "geo_bounding_box": {
                    self.field_name: bbox
                }
            })
        return search
