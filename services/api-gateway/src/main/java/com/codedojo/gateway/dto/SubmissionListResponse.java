package com.codedojo.gateway.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record SubmissionListResponse(
        List<SubmissionResponse> items,
        int page,
        @JsonProperty("page_size") int pageSize,
        int total
) {
}
