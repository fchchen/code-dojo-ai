package com.codedojo.gateway.dto;

import jakarta.validation.constraints.NotBlank;

public record AuthRequest(@NotBlank String username) {
}
