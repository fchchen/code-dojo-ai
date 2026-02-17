package com.codedojo.gateway.controller;

import com.codedojo.gateway.dto.AuthRequest;
import com.codedojo.gateway.dto.AuthResponse;
import com.codedojo.gateway.security.JwtProvider;
import com.codedojo.gateway.service.DemoAuthRateLimiter;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.server.reactive.ServerHttpRequest;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final JwtProvider jwtProvider;
    private final DemoAuthRateLimiter demoAuthRateLimiter;

    public AuthController(JwtProvider jwtProvider, DemoAuthRateLimiter demoAuthRateLimiter) {
        this.jwtProvider = jwtProvider;
        this.demoAuthRateLimiter = demoAuthRateLimiter;
    }

    @PostMapping("/demo")
    @ResponseStatus(HttpStatus.CREATED)
    public AuthResponse demoLogin(@Valid @RequestBody AuthRequest request, ServerHttpRequest serverHttpRequest) {
        if (!demoAuthRateLimiter.allow(serverHttpRequest)) {
            throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS, "demo auth rate limit exceeded");
        }
        String token = jwtProvider.generateToken(request.username());
        return new AuthResponse(token, request.username(), jwtProvider.getExpirationSeconds());
    }
}
