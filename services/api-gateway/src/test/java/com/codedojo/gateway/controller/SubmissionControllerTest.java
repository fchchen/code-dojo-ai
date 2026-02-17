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
        properties = "app.jwt.secret=UnitTestSecretKeyForJwtSigning_AtLeast32Chars"
)
@AutoConfigureWebTestClient
class SubmissionControllerTest {
    @Autowired
    private WebTestClient webTestClient;

    @Test
    void returnsUnauthorizedWithoutToken() {
        webTestClient.post()
                .uri("/api/submissions")
                .bodyValue(Map.of("code", "print('x')", "language", "python"))
                .exchange()
                .expectStatus().isUnauthorized();
    }
}
