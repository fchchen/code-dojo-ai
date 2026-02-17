package com.codedojo.gateway.dto;

import java.util.Map;

public record HealthResponse(
        String status,
        Map<String, String> services,
        String timestamp
) {
}
