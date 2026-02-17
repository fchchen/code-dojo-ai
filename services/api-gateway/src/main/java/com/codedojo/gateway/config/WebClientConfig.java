package com.codedojo.gateway.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {
    @Bean
    public WebClient coachAgentWebClient(
            @Value("${app.services.coach-agent-url}") String baseUrl,
            WebClient.Builder builder
    ) {
        return builder
                .baseUrl(baseUrl)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }

    @Bean
    public WebClient mlAnalyzerWebClient(
            @Value("${app.services.ml-analyzer-url}") String baseUrl,
            WebClient.Builder builder
    ) {
        return builder
                .baseUrl(baseUrl)
                .build();
    }
}
