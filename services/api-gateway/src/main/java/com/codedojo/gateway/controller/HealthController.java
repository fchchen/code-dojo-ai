package com.codedojo.gateway.controller;

import com.codedojo.gateway.dto.HealthResponse;
import com.codedojo.gateway.service.HealthAggregator;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/health")
public class HealthController {
    private final HealthAggregator healthAggregator;

    public HealthController(HealthAggregator healthAggregator) {
        this.healthAggregator = healthAggregator;
    }

    @GetMapping
    public Mono<HealthResponse> health() {
        return healthAggregator.aggregateHealth();
    }
}
