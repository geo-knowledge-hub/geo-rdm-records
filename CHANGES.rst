..
    Copyright (C) 2022 Geo Secretariat.

    geo-rdm-records is free software; you can redistribute it and/or modify
    it under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 0.4.0 (2023-01-05)
--------------------------

- Revised Package structure;
- Added initial implementation of the Packages API
  
  - Metadata management
  - Files management;
  - Relationship between packages and resources revised;
  - Package context to manage resources in a package and its versions.

- Revised customization module for Invenio RDM Records;
- Introduced Management Dashboard for Knowledge Packages;
- Introduced a search endpoint to enable users to find Packages and Resources simultaneously.

Version 0.3.1 (2022-07-19)
--------------------------

- Updated `Invenio Geographic Identifiers <https://github.com/geo-knowledge-hub/invenio-geographic-identifiers>`_ to version `v0.1.1 <https://github.com/geo-knowledge-hub/invenio-geographic-identifiers/releases/tag/v0.1.1>`_.

Version 0.3.0 (2022-07-17)
--------------------------

- Initial spatial support

  - Added initial support for spatial search via Search Filters arguments (``bbox`` filter);
  - Extended the supported Geometry types in the Record Metadata (``Knowledge Package`` and ``Knowledge Resource``):

    - `Point <https://tools.ietf.org/html/rfc7946#section-3.1.2>`_ (from ``InvenioRDM``)
    - `MultiPoint <https://tools.ietf.org/html/rfc7946#section-3.1.3>`_ (from ``InvenioRDM``)
    - `Polygon <https://tools.ietf.org/html/rfc7946#section-3.1.6>`_ (from ``InvenioRDM``)
    - `MultiPolygon <https://tools.ietf.org/html/rfc7946#section-3.1.7>`_ (New feature);
    - `LineString <https://tools.ietf.org/html/rfc7946#section-3.1.4>`_ (New feature);
    - `MultiLineString <https://tools.ietf.org/html/rfc7946#section-3.1.5>`_ (New feature);
    - `GeometryCollection <https://tools.ietf.org/html/rfc7946#section-3.1.8>`_ (New feature).
    
  - Added Geographic Identifiers vocabularies via integration with the `Invenio Geographic Identifiers <https://github.com/geo-knowledge-hub/invenio-geographic-identifiers>`_ module.

Version 0.2.0 (2022-04-24)
--------------------------

- Initial public release
- Custom fields for the Record (Draft and Record) data model. In this version, the following new fields are supported on Record objects:

  - Target Audiences
  - GEO Work Programme Activities
  - Engagement Priorities
- Faceted search support for the new Record fields;
- Custom Resource Serializer (based on `Invenio RDM Records <https://github.com/inveniosoftware/invenio-rdm-records>`_) to handle the custom fields.
