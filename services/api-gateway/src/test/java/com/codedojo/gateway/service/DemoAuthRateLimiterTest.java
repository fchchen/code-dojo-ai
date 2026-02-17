package com.codedojo.gateway.service;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.mock.http.server.reactive.MockServerHttpRequest;

import java.net.InetSocketAddress;

class DemoAuthRateLimiterTest {
    @Test
    void ignoresForwardedForWhenTrustDisabled() {
        DemoAuthRateLimiter limiter = new DemoAuthRateLimiter(1, false, "127.0.0.1,::1");

        var requestOne = MockServerHttpRequest.post("/api/auth/demo")
                .remoteAddress(new InetSocketAddress("127.0.0.1", 5000))
                .header("X-Forwarded-For", "198.51.100.10")
                .build();
        var requestTwo = MockServerHttpRequest.post("/api/auth/demo")
                .remoteAddress(new InetSocketAddress("127.0.0.1", 5001))
                .header("X-Forwarded-For", "203.0.113.20")
                .build();

        Assertions.assertTrue(limiter.allow(requestOne));
        Assertions.assertFalse(limiter.allow(requestTwo));
    }

    @Test
    void usesForwardedForOnlyForTrustedProxy() {
        DemoAuthRateLimiter limiter = new DemoAuthRateLimiter(1, true, "127.0.0.1,::1");

        var requestOne = MockServerHttpRequest.post("/api/auth/demo")
                .remoteAddress(new InetSocketAddress("127.0.0.1", 6000))
                .header("X-Forwarded-For", "198.51.100.10")
                .build();
        var requestTwo = MockServerHttpRequest.post("/api/auth/demo")
                .remoteAddress(new InetSocketAddress("127.0.0.1", 6001))
                .header("X-Forwarded-For", "203.0.113.20")
                .build();

        Assertions.assertTrue(limiter.allow(requestOne));
        Assertions.assertTrue(limiter.allow(requestTwo));
    }

    @Test
    void ignoresForwardedForFromUntrustedProxy() {
        DemoAuthRateLimiter limiter = new DemoAuthRateLimiter(1, true, "127.0.0.1,::1");

        var requestOne = MockServerHttpRequest.post("/api/auth/demo")
                .remoteAddress(new InetSocketAddress("10.0.0.10", 7000))
                .header("X-Forwarded-For", "198.51.100.10")
                .build();
        var requestTwo = MockServerHttpRequest.post("/api/auth/demo")
                .remoteAddress(new InetSocketAddress("10.0.0.10", 7001))
                .header("X-Forwarded-For", "203.0.113.20")
                .build();

        Assertions.assertTrue(limiter.allow(requestOne));
        Assertions.assertFalse(limiter.allow(requestTwo));
    }
}
