package com.codedojo.gateway.config;

import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class ObservationConfig {
    @Bean
    public WebClient.Builder webClientBuilder(MeterRegistry registry) {
        return WebClient.builder();
    }
}
