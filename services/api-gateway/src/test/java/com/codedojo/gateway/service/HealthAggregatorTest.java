package com.codedojo.gateway.service;

import com.codedojo.gateway.dto.HealthResponse;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.web.reactive.function.client.WebClient;

class HealthAggregatorTest {
    @Test
    void aggregatesAsDegradedWhenUpstreamsMissing() {
        WebClient coach = WebClient.builder().baseUrl("http://127.0.0.1:65535").build();
        WebClient ml = WebClient.builder().baseUrl("http://127.0.0.1:65534").build();
        HealthAggregator aggregator = new HealthAggregator(coach, ml);

        HealthResponse response = aggregator.aggregateHealth().block();
        Assertions.assertNotNull(response);
        Assertions.assertEquals("degraded", response.status());
    }
}
