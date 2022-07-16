# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Location schema definition."""

from functools import partial

from flask import current_app
from geojson import LineString, MultiLineString, MultiPolygon
from marshmallow import Schema
from marshmallow.fields import Constant, Float, List, Nested
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.schemas import GeometryObjectSchema as BaseGeometryObjectSchema
from marshmallow_utils.schemas import (
    IdentifierSchema,
    MultiPointSchema,
    PointSchema,
    PolygonSchema,
)
from marshmallow_utils.schemas.geojson import GeometryValidator
from werkzeug.local import LocalProxy

record_location_schemes = LocalProxy(
    lambda: current_app.config["RDM_RECORDS_LOCATION_SCHEMES"]
)


class LineStringSchema(Schema):
    """GeoJSON LineString schema.

    See:
        LineString definition on GeoJSON Specification (https://tools.ietf.org/html/rfc7946#section-3.1.4)
    """

    coordinates = List(
        List(Float, required=True),
        required=True,
        validate=GeometryValidator(LineString),
    )

    type = Constant("LineString")


class MultiLineStringSchema(Schema):
    """GeoJSON LineString schema.

    See:
        MultiLineString definition on GeoJSON Specification (https://tools.ietf.org/html/rfc7946#section-3.1.5)
    """

    coordinates = List(
        List(List(Float, required=True)),
        required=True,
        validate=GeometryValidator(MultiLineString),
    )

    type = Constant("MultiLineString")


class MultiPolygonSchema(Schema):
    """GeoJSON MultiPolygon schema.

    See https://tools.ietf.org/html/rfc7946#section-3.1.7
    """

    coordinates = List(
        List(List(List(Float, required=True))),
        required=True,
        validate=GeometryValidator(MultiPolygon),
    )

    type = Constant("MultiPolygon")


class GeometriesSchema(BaseGeometryObjectSchema):
    """Schema to define multiple GeoJSON Geometry support."""

    type_schemas = {
        "Point": PointSchema,
        "MultiPoint": MultiPointSchema,
        "Polygon": PolygonSchema,
        "MultiPolygon": MultiPolygonSchema,
        "LineString": LineStringSchema,
        "MultiLineString": MultiLineStringSchema,
    }


class GeometryCollectionSchema(Schema):
    """GeoJSON GeometryCollection schema.

    See https://tools.ietf.org/html/rfc7946#section-3.1.8
    """

    geometries = List(Nested(GeometriesSchema), required=True)

    type = Constant("GeometryCollection")


class GeometryObjectSchema(BaseGeometryObjectSchema):
    """GeoJSON Object schema."""

    type_schemas = {
        "Point": PointSchema,
        "MultiPoint": MultiPointSchema,
        "Polygon": PolygonSchema,
        "MultiPolygon": MultiPolygonSchema,
        "LineString": LineStringSchema,
        "MultiLineString": MultiLineStringSchema,
        "GeometryCollection": GeometryCollectionSchema,
    }


class LocationSchema(Schema):
    """Location schema."""

    place = SanitizedUnicode()

    identifiers = List(
        Nested(partial(IdentifierSchema, allowed_schemes=record_location_schemes))
    )

    description = SanitizedUnicode()

    geometry = Nested(GeometryObjectSchema)


class FeatureSchema(Schema):
    """Location feature schema."""

    features = List(Nested(LocationSchema))
