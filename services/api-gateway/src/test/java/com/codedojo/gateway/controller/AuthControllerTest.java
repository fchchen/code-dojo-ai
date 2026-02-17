package com.codedojo.gateway.controller;

import com.codedojo.gateway.GatewayApplication;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.reactive.server.WebTestClient;

import java.util.Map;

@SpringBootTest(classes = GatewayApplication.class)
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
}
