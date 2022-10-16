/*
 * This file is part of Geo Secretariat.
 * Copyright (C) 2022 GEO Secretariat.
 *
 * GEO-RDM-Records is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

export const packageErrorSerializer = (error) => ({
  message: error?.response?.data?.message,
  errors: error?.response?.data?.errors,
  status: error?.response?.data?.status,
});
