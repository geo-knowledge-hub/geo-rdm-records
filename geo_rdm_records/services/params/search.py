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
        raise QuerystringValidationError(
            "Point used to created the bounding box is not valid", point.errors()
        )

    # ToDo: Check 180th meridian cases
    if (lat < -90.0) or (lat > 90.0):
        raise QuerystringValidationError("latitude is out-of range [-90, 90]")

    if (lon < -180.0) or (lon > 180.0):
        raise QuerystringValidationError("longitude is out-of range [-180, 180]")


def generate_bounding_box(value: str):
    """Generate and validate a Bounding Box object from a string.

    Args:
        value (str): Query string value to be transformed in a bounding box object.
                     This string must have be defined with 2 points:

                        (Top Left Point, Bottom Right Point)

                     The definition of these points must be done in an array with the following structure:

                        (Longitude, Latitude, Longitude, Latitude)

    Returns:
        List[Tuple]: Bounding box object.

    Example:
        >>> my_bbox_string = '-80.4638671875,19.601194161263145,-73.7841796875,15.11455287'
        >>> generate_bounding_box(my_bbox_string) # [[-80.4638671875,19.601194161263145], [-73.7841796875,15.11455287]]
    """
    try:
        # try parsing the `value` in a list
        bbox = value.split(",") or []

        # transforming the values in float
        bbox = list(map(float, bbox))
    except ValueError:
        raise QuerystringValidationError(
            "You must define the bounding box parameter using only numeric values."
        )
    except BaseException:
        raise QuerystringValidationError("Invalid bounding box definition.")

    if len(bbox) != 4:
        raise QuerystringValidationError(
            "A bounding box must be defined "
            "by 2 Point (TopLeft, BottomRight). "
            "This is represented by a array with "
            "four elements: [lon, lat, lon, lat]"
        )

    # validating the bounding box points
    list(
        map(
            lambda x: _validate_point_coordinates(x),
            [Point(bbox[0:2]), Point(bbox[2:])],
        )
    )

    return bbox


class BoundingBoxParam(ParamInterpreter):
    """Evaluates the 'filters.bbox' parameter.

    Note:
        The `BoundingBoxParam` interpreter is an initial (and probably temporary)
        solution to allow users to perform spatial queries using the bounding box.

        In the future, we will implement specific spatial operators, which will be
        provided in a specific API.
    """

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

        # getting the filters available
        filters = params.get("filters") or {}

        # checking if the bbox filter is used
        bbox = filters.get("bbox")

        if bbox:
            bbox = generate_bounding_box(bbox)

            # creating the filter.
            search = search.filter(
                "geo_shape",
                **{
                    self.field_name: {
                        "shape": {
                            "type": "envelope",
                            "coordinates": [bbox[0:2], bbox[2:]],
                        },
                        "relation": "intersects",
                    }
                }
            )
        return search
