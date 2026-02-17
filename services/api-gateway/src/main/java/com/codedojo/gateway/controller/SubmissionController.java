package com.codedojo.gateway.controller;

import com.codedojo.gateway.dto.SubmissionRequest;
import com.codedojo.gateway.service.CoachAgentService;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
@RequestMapping("/api/submissions")
public class SubmissionController {
    private final CoachAgentService coachAgentService;

    public SubmissionController(CoachAgentService coachAgentService) {
        this.coachAgentService = coachAgentService;
    }

    @PostMapping
    public Mono<Map<String, Object>> createSubmission(
            @Valid @RequestBody SubmissionRequest request,
            Authentication authentication
    ) {
        return coachAgentService.createSubmission(request, authentication.getName());
    }

    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> streamSubmission(
            @Valid @RequestBody SubmissionRequest request,
            Authentication authentication
    ) {
        return coachAgentService.streamSubmission(request, authentication.getName());
    }

    @GetMapping("/{id}")
    public Mono<Map<String, Object>> getSubmission(@PathVariable String id) {
        return coachAgentService.getSubmission(id);
    }

    @GetMapping
    public Mono<Map<String, Object>> listSubmissions(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int pageSize
    ) {
        return coachAgentService.listSubmissions(page, pageSize);
    }
}
