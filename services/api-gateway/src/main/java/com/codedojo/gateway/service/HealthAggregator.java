package com.codedojo.gateway.service;

import com.codedojo.gateway.dto.HealthResponse;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.time.Instant;
import java.util.Map;

@Service
public class HealthAggregator {
    private final WebClient coachAgentWebClient;
    private final WebClient mlAnalyzerWebClient;

    public HealthAggregator(WebClient coachAgentWebClient, WebClient mlAnalyzerWebClient) {
        this.coachAgentWebClient = coachAgentWebClient;
        this.mlAnalyzerWebClient = mlAnalyzerWebClient;
    }

    public Mono<HealthResponse> aggregateHealth() {
        Mono<String> coach = coachAgentWebClient.get()
                .uri("/health")
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .map(this::coachStatus)
                .onErrorReturn("unhealthy")
                .timeout(Duration.ofSeconds(4), Mono.just("unhealthy"));

        Mono<String> ml = mlAnalyzerWebClient.get()
                .uri("/health")
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .map(this::mlAnalyzerStatus)
                .onErrorReturn("unhealthy")
                .timeout(Duration.ofSeconds(4), Mono.just("unhealthy"));

        return Mono.zip(coach, ml)
                .map(tuple -> {
                    String coachStatus = tuple.getT1();
                    String mlStatus = tuple.getT2();
                    String status = ("healthy".equals(coachStatus) && "healthy".equals(mlStatus)) ? "healthy" : "degraded";
                    return new HealthResponse(
                            status,
                            Map.of("coachAgent", coachStatus, "mlAnalyzer", mlStatus),
                            Instant.now().toString()
                    );
                });
    }

    private String coachStatus(Map<String, Object> payload) {
        Object status = payload.get("status");
        return "healthy".equals(status) ? "healthy" : "degraded";
    }

    private String mlAnalyzerStatus(Map<String, Object> payload) {
        Object status = payload.get("status");
        Object ready = payload.get("models_ready");
        if ("healthy".equals(status) && Boolean.TRUE.equals(ready)) {
            return "healthy";
        }
        return "degraded";
    }
}
