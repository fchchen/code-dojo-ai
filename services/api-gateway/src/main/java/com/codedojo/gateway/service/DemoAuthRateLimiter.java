package com.codedojo.gateway.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;

import java.net.InetSocketAddress;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class DemoAuthRateLimiter {
    private static final long WINDOW_MILLIS = 60_000L;
    private final int maxRequestsPerMinute;
    private final ConcurrentHashMap<String, WindowCounter> counters = new ConcurrentHashMap<>();

    public DemoAuthRateLimiter(@Value("${app.auth.demo-rate-limit-per-minute:30}") int maxRequestsPerMinute) {
        this.maxRequestsPerMinute = Math.max(1, maxRequestsPerMinute);
    }

    public boolean allow(ServerHttpRequest request) {
        long now = System.currentTimeMillis();
        String key = resolveClientKey(request);
        WindowCounter counter = counters.computeIfAbsent(key, unused -> new WindowCounter(now));
        return counter.tryConsume(now, maxRequestsPerMinute);
    }

    private String resolveClientKey(ServerHttpRequest request) {
        String forwardedFor = request.getHeaders().getFirst("X-Forwarded-For");
        if (forwardedFor != null && !forwardedFor.isBlank()) {
            String[] parts = forwardedFor.split(",");
            if (parts.length > 0 && !parts[0].isBlank()) {
                return parts[0].trim();
            }
        }
        InetSocketAddress remoteAddress = request.getRemoteAddress();
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
    }
}
