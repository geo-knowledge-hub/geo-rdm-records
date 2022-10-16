/*
 * This file is part of Geo Secretariat.
 * Copyright (C) 2022 GEO Secretariat.
 *
 * GEO-RDM-Records is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { http } from "./config";

/**
 * API Client for Packages API.
 *
 */
export class PackagesAPI {
  baseUrl = "/api/packages";

  /**
   * Update a pre-existing package context.
   *
   * @param {string} packageId - identifier
   * @param {object} payload - Package context definitions
   * @param {object} options - Custom options
   */
  async updateContext(packageId, payload, options) {
    options = options || {};
    return http.put(`${this.baseUrl}/${packageId}/context`, payload, {
      ...options,
    });
  }
}
