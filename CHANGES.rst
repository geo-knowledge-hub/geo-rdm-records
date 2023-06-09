..
    Copyright (C) 2022 Geo Secretariat.

    geo-rdm-records is free software; you can redistribute it and/or modify
    it under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 0.5.0 (2023-06-08)
--------------------------

- Packages API

  - Fixed Context Manager references in the service layer;

  - Added tasks to register PID (External) in the Knowledge Packages;

  - Fixed broken links on the Packages Dashboard page.

- Requests for Packages API

  - Added request service for `feed posts <https://gkhub.earthobservations.org/feed>`_. System based on `Invenio Requests <https://inveniordm.docs.cern.ch/develop/architecture/requests/>`_ module;

  - Requests implemented with basic e-mail support;

- Security

  - Added `IfPackage` generator


Version 0.5.0 (2023-03-01)
--------------------------

- Updated to be compatible with `InvenioRDM 11 <https://inveniordm.docs.cern.ch/releases/versions/version-v11.0.0/>`_;

- Packages API

  - Updated Funders/Awards schema (`#119 <https://github.com/geo-knowledge-hub/geo-rdm-records/issues/119>`_);
  - Added improvements on the Package management (create, update, delete, associate resources, share).

- Invenio RDM Records customization layer

  - Upgrading Records API to be compatible with new the OAI-PMH server version (InvenioRDM 11 compatible);
  - Fixed missing values in the Record serialization (`#132 <https://github.com/geo-knowledge-hub/geo-rdm-records/issues/132>`_).

- Search API

  - Mapping documents reviewed (`#124 <https://github.com/geo-knowledge-hub/geo-rdm-records/issues/124>`_).

- Security

  - Reviewed file permissions to work with Invenio S3.

- Elasticsearch mapping and structure replaced by OpenSearch.


Version 0.4.0 (2023-01-05)
--------------------------

- Revised Package structure;
- Added initial implementation of the Packages API
  
  - Metadata management;
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
