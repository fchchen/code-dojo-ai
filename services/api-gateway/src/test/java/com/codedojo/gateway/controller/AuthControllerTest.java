package com.codedojo.gateway.controller;

import com.codedojo.gateway.GatewayApplication;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.reactive.server.WebTestClient;

import java.util.Map;

@SpringBootTest(
        classes = GatewayApplication.class,
        properties = {
                "app.jwt.secret=UnitTestSecretKeyForJwtSigning_AtLeast32Chars",
                "app.auth.demo-rate-limit-per-minute=1"
        }
)
@AutoConfigureWebTestClient
class AuthControllerTest {
    @Autowired
    private WebTestClient webTestClient;

    @Test
    void returnsTokenForDemoAuth() {
        webTestClient.post()
                .uri("/api/auth/demo")
                .bodyValue(Map.of("username", "demo"))
                .exchange()
                .expectStatus().isCreated()
                .expectBody()
                .jsonPath("$.token").isNotEmpty()
                .jsonPath("$.username").isEqualTo("demo");
    }

    @Test
    void rateLimitsDemoAuthByClientIp() {
        webTestClient.post()
                .uri("/api/auth/demo")
                .header("X-Forwarded-For", "198.51.100.10")
                .bodyValue(Map.of("username", "demo1"))
                .exchange()
                .expectStatus().isCreated();

        webTestClient.post()
                .uri("/api/auth/demo")
                .header("X-Forwarded-For", "198.51.100.10")
                .bodyValue(Map.of("username", "demo2"))
                .exchange()
                .expectStatus().isEqualTo(429);
    }
}
