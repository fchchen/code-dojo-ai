package com.codedojo.gateway.service;

import com.codedojo.gateway.dto.CoachSubmissionRequest;
import com.codedojo.gateway.dto.SubmissionListResponse;
import com.codedojo.gateway.dto.SubmissionRequest;
import com.codedojo.gateway.dto.SubmissionResponse;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.http.codec.ServerSentEvent;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Duration;

@Service
public class CoachAgentService {
    private final WebClient coachAgentWebClient;

    public CoachAgentService(WebClient coachAgentWebClient) {
        this.coachAgentWebClient = coachAgentWebClient;
    }

    public Mono<SubmissionResponse> createSubmission(SubmissionRequest request, String username) {
        CoachSubmissionRequest payload = new CoachSubmissionRequest(request.code(), request.language(), username);

        return coachAgentWebClient.post()
                .uri("/api/submissions")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(payload)
                .retrieve()
                .bodyToMono(SubmissionResponse.class)
                .timeout(Duration.ofSeconds(30));
    }

    public Flux<ServerSentEvent<String>> streamSubmission(SubmissionRequest request, String username) {
        CoachSubmissionRequest payload = new CoachSubmissionRequest(request.code(), request.language(), username);

        return coachAgentWebClient.post()
                .uri("/api/submissions/stream")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .bodyValue(payload)
                .retrieve()
                .bodyToFlux(new ParameterizedTypeReference<ServerSentEvent<String>>() {})
                .map(event -> ServerSentEvent.<String>builder()
                        .event(event.event() == null ? "message" : event.event())
                        .data(event.data() == null ? "{}" : event.data())
                        .build())
                .timeout(Duration.ofSeconds(45));
    }

    public Mono<SubmissionResponse> getSubmission(String id) {
        return coachAgentWebClient.get()
                .uri("/api/submissions/{id}", id)
                .retrieve()
                .bodyToMono(SubmissionResponse.class)
                .timeout(Duration.ofSeconds(15));
    }

    public Mono<SubmissionListResponse> listSubmissions(int page, int pageSize) {
        return coachAgentWebClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/submissions")
                        .queryParam("page", page)
                        .queryParam("page_size", pageSize)
                        .build())
                .retrieve()
                .bodyToMono(SubmissionListResponse.class)
                .timeout(Duration.ofSeconds(15));
    }
}
