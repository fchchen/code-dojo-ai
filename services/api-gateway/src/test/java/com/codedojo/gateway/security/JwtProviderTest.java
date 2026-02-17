package com.codedojo.gateway.security;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class JwtProviderTest {
    @Test
    void generatesAndValidatesToken() {
        JwtProvider provider = new JwtProvider("UnitTestSecretKeyForJwtSigning_AtLeast32Chars", 3600);
        String token = provider.generateToken("demo-user");

        var username = provider.validateAndGetUsername(token);
        Assertions.assertTrue(username.isPresent());
        Assertions.assertEquals("demo-user", username.get());
    }

    @Test
    void rejectsInvalidToken() {
        JwtProvider provider = new JwtProvider("UnitTestSecretKeyForJwtSigning_AtLeast32Chars", 3600);
        var username = provider.validateAndGetUsername("invalid.token.value");
        Assertions.assertTrue(username.isEmpty());
    }
}
