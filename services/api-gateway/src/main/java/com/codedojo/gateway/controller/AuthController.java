package com.codedojo.gateway.controller;

import com.codedojo.gateway.dto.AuthRequest;
import com.codedojo.gateway.dto.AuthResponse;
import com.codedojo.gateway.security.JwtProvider;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final JwtProvider jwtProvider;

    public AuthController(JwtProvider jwtProvider) {
        this.jwtProvider = jwtProvider;
    }

    @PostMapping("/demo")
    @ResponseStatus(HttpStatus.CREATED)
    public AuthResponse demoLogin(@Valid @RequestBody AuthRequest request) {
        String token = jwtProvider.generateToken(request.username());
        return new AuthResponse(token, request.username(), jwtProvider.getExpirationSeconds());
    }
}
