package com.codedojo.gateway.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;

import java.net.InetSocketAddress;
import java.util.Arrays;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Component
public class DemoAuthRateLimiter {
    private static final long WINDOW_MILLIS = 60_000L;
    private static final long STALE_ENTRY_MILLIS = WINDOW_MILLIS * 3;
    private final int maxRequestsPerMinute;
    private final boolean trustForwardedHeaders;
    private final Set<String> trustedProxies;
    private final ConcurrentHashMap<String, WindowCounter> counters = new ConcurrentHashMap<>();
    private volatile long lastCleanupMillis = System.currentTimeMillis();

    public DemoAuthRateLimiter(
            @Value("${app.auth.demo-rate-limit-per-minute:30}") int maxRequestsPerMinute,
            @Value("${app.auth.trust-forwarded-headers:false}") boolean trustForwardedHeaders,
            @Value("${app.auth.trusted-proxies:127.0.0.1,::1}") String trustedProxiesCsv
    ) {
        this.maxRequestsPerMinute = Math.max(1, maxRequestsPerMinute);
        this.trustForwardedHeaders = trustForwardedHeaders;
        this.trustedProxies = Arrays.stream(trustedProxiesCsv.split(","))
                .map(String::trim)
                .filter(value -> !value.isEmpty())
                .collect(Collectors.toSet());
    }

    public boolean allow(ServerHttpRequest request) {
        long now = System.currentTimeMillis();
        String key = resolveClientKey(request);
        maybeCleanup(now);
        WindowCounter counter = counters.computeIfAbsent(key, unused -> new WindowCounter(now));
        return counter.tryConsume(now, maxRequestsPerMinute);
    }

    private String resolveClientKey(ServerHttpRequest request) {
        InetSocketAddress remoteAddress = request.getRemoteAddress();
        String remoteIp = extractRemoteIp(remoteAddress);
        if (trustForwardedHeaders && trustedProxies.contains(remoteIp)) {
            String forwardedFor = request.getHeaders().getFirst("X-Forwarded-For");
            if (forwardedFor != null && !forwardedFor.isBlank()) {
                String[] parts = forwardedFor.split(",");
                if (parts.length > 0 && !parts[0].isBlank()) {
                    return parts[0].trim();
                }
            }
        }
        return remoteIp;
    }

    private void maybeCleanup(long nowMillis) {
        if (nowMillis - lastCleanupMillis < WINDOW_MILLIS) {
            return;
        }
        lastCleanupMillis = nowMillis;
        counters.entrySet().removeIf(entry -> nowMillis - entry.getValue().windowStartMillis() >= STALE_ENTRY_MILLIS);
    }

    private String extractRemoteIp(InetSocketAddress remoteAddress) {
        if (remoteAddress == null) {
            return "unknown";
        }
        if (remoteAddress.getAddress() != null) {
            return remoteAddress.getAddress().getHostAddress();
        }
        return remoteAddress.getHostString();
    }

    private static class WindowCounter {
        private long windowStartMillis;
        private int count;

        private WindowCounter(long nowMillis) {
            this.windowStartMillis = nowMillis;
            this.count = 0;
        }

        private synchronized boolean tryConsume(long nowMillis, int limitPerWindow) {
            if (nowMillis - windowStartMillis >= WINDOW_MILLIS) {
                windowStartMillis = nowMillis;
                count = 0;
            }
            if (count >= limitPerWindow) {
                return false;
            }
            count += 1;
            return true;
        }

        private synchronized long windowStartMillis() {
            return windowStartMillis;
        }
    }
}
