package com.codedojo.gateway.config;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.support.WebExchangeBindException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(WebExchangeBindException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(WebExchangeBindException ex) {
        Map<String, String> errors = new HashMap<>();
        for (FieldError error : ex.getFieldErrors()) {
            errors.put(error.getField(), error.getDefaultMessage());
        }
        return ResponseEntity.badRequest().body(Map.of("error", "validation_failed", "fields", errors));
    }

    @ExceptionHandler(WebClientRequestException.class)
    public ResponseEntity<Map<String, String>> handleUpstreamConnection(WebClientRequestException ex) {
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(Map.of("error", "upstream_unavailable", "message", ex.getMessage()));
    }

    @ExceptionHandler(WebClientResponseException.class)
    public ResponseEntity<Map<String, String>> handleUpstreamResponse(WebClientResponseException ex) {
        HttpStatus status = ex.getStatusCode().is5xxServerError() ? HttpStatus.BAD_GATEWAY : HttpStatus.BAD_REQUEST;
        return ResponseEntity.status(status)
                .body(Map.of("error", "upstream_error", "message", ex.getResponseBodyAsString()));
    }
}
