package com.codedojo.gateway.dto;

public record CoachSubmissionRequest(
        String code,
        String language,
        String username
) {
}
