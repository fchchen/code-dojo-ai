package com.codedojo.gateway.controller;

import com.codedojo.gateway.GatewayApplication;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.reactive.server.WebTestClient;

@SpringBootTest(
        classes = GatewayApplication.class,
        properties = "app.jwt.secret=UnitTestSecretKeyForJwtSigning_AtLeast32Chars"
)
@AutoConfigureWebTestClient
class SecurityConfigTest {
    @Autowired
    private WebTestClient webTestClient;

    @Test
    void healthIsPublic() {
        webTestClient.get()
                .uri("/api/health")
                .exchange()
                .expectStatus().is2xxSuccessful();
    }

    @Test
    void submissionsRequireAuth() {
        webTestClient.get()
                .uri("/api/submissions")
                .exchange()
                .expectStatus().isUnauthorized();
    }
}
