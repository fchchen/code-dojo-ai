package com.codedojo.gateway.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record CoachingResultResponse(
        String summary,
        int score,
        List<String> issues,
        @JsonProperty("improved_code") String improvedCode,
        @JsonProperty("best_practices") List<String> bestPractices,
        @JsonProperty("concept_explanation") String conceptExplanation
) {
}
