package com.codedojo.gateway.dto;

public record AuthResponse(String token, String username, long expiresIn) {
}
