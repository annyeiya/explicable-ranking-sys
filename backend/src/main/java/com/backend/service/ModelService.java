package com.backend.service;

import com.backend.model.AggregatedResult;
import com.backend.model.ModelResponse;
import com.backend.model.ModelResponseWrapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.ExchangeStrategies;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class ModelService {

    private final WebClient webClient;

    @Value("${model.service.endpoint}")
    private String modelEndpoint;

    @Value("${aggregation.top_k_org}")
    private int topKOrg;

    @Value("${aggregation.top_k_func}")
    private int topKFunc;

    public ModelService(@Value("${model.service.url}") String modelBaseUrl) {
        ExchangeStrategies strategies = ExchangeStrategies.builder()
                .codecs(configurer -> configurer.defaultCodecs()
                        .maxInMemorySize(10 * 1024 * 1024)) // 10 MB
                .build();

        this.webClient = WebClient.builder()
                .baseUrl(modelBaseUrl)
                .exchangeStrategies(strategies)
                .clientConnector(new ReactorClientHttpConnector(HttpClient.create()))
                .build();
    }

    public List<ModelResponse> sendRequestToModel(String text) {
        try {
            Map<String, String> requestBody = Map.of("text", text);

            Mono<ModelResponseWrapper> response = webClient.post()
                    .uri(modelEndpoint)
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(ModelResponseWrapper.class);

            ModelResponseWrapper wrapper = response.block();
            return wrapper == null ? List.of() : wrapper.getResult();
        } catch (Exception e) {
            System.out.println("[ERROR] while calling model: " + e.getMessage());
            return List.of();
        }
    }

    public List<AggregatedResult> aggregateByOrgan(List<ModelResponse> responses) {
        Map<String, List<ModelResponse>> byPhrase = responses.stream()
                .collect(Collectors.groupingBy(ModelResponse::getTextPhrase));

        List<ModelResponse> topFuncPerPhrase = byPhrase.values().stream()
                .flatMap(list -> list.stream()
                        .sorted(Comparator.comparingDouble(ModelResponse::getSimilarity)
                                .reversed())
                        .limit(topKFunc)
                )
                .toList();

        Map<String, List<ModelResponse>> byOrgan = topFuncPerPhrase.stream()
                .collect(Collectors.groupingBy(ModelResponse::getOrg));

        List<AggregatedResult> aggregated = new ArrayList<>();
        Map<String, Double> orgBoosts = new HashMap<>();

        for (var entry : byOrgan.entrySet()) {
            String organ = entry.getKey();
            List<ModelResponse> items = entry.getValue();

            double sum = items.stream().mapToDouble(ModelResponse::getSimilarity).sum();
            double totalScore = sum / items.size() * 0.7 + items.size() * 0.3;

            double contextBoost = items.get(0).getContextBoost();
            orgBoosts.put(organ, contextBoost);

            List<AggregatedResult.MatchInfo> matches = items.stream()
                    .sorted(Comparator.comparing(ModelResponse::getSimilarity).reversed())
                    .map(i -> new AggregatedResult.MatchInfo(
                            i.getTextPhrase(), i.getFunction(), i.getSimilarity()))
                    .toList();

            aggregated.add(new AggregatedResult(
                    organ,
                    Math.round(totalScore * 1000.0) / 1000.0,
                    matches
            ));
        }

        List<Map.Entry<String, Double>> sortedBoosts = orgBoosts.entrySet().stream()
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .toList();

        Map<String, Double> boostWeights = new HashMap<>();
        for (int i = 0; i < sortedBoosts.size(); i++) {
            String org = sortedBoosts.get(i).getKey();
            double weight = switch (i) {
                case 0 -> 0.3;
                case 1 -> 0.2;
                case 2 -> 0.1;
                default -> 0.0;
            };
            boostWeights.put(org, weight);
        }
        System.out.println(boostWeights);

        return aggregated.stream()
                .map(r -> {
                    double boost = boostWeights.getOrDefault(r.getOrg(), 0.0);
                    double finalScore = Math.round((r.getTotalScore() + boost) * 1000.0) / 1000.0;
                    return new AggregatedResult(r.getOrg(), finalScore, r.getMatchedPhrases());
                })
                .sorted(Comparator.comparingDouble(AggregatedResult::getTotalScore)
                        .reversed())
                .limit(topKOrg)
                .toList();
    }

    public List<AggregatedResult> sendToModelAndAggregate(String text) {
        List<ModelResponse> responses = sendRequestToModel(text);
        return aggregateByOrgan(responses);
    }

}
