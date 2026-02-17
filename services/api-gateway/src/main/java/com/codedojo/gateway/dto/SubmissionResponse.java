package com.codedojo.gateway.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record SubmissionResponse(
        String id,
        String username,
        String language,
        String status,
        CoachingResultResponse result,
        String error,
        @JsonProperty("created_at") String createdAt,
        @JsonProperty("updated_at") String updatedAt
) {
}
