/*
 * This file is part of Geo Secretariat.
 * Copyright (C) 2022 GEO Secretariat.
 *
 * GEO-RDM-Records is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";

import { i18next } from "@translations/geo_rdm_records/i18next";

import { Grid, Header, Segment, Container, Icon } from "semantic-ui-react";

export const NotImplementedMessage = () => {
  return (
    <Container className="rel-pt-2">
      <Grid>
        <Grid.Row fluid centered>
          <Grid.Column width={16} verticalAlign={"center"}>
            <Segment placeholder size={"large"}>
              <Header icon>
                <Icon name="clock outline" />
                {i18next.t("This feature will be available soon.")}
              </Header>
            </Segment>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Container>
  );
};
