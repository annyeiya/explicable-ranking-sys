package com.backend.model;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
@Data
@AllArgsConstructor
public class AggregatedResult {
    private String org;
    private double totalScore;
    private List<MatchInfo> matchedPhrases;

    @Data
    @AllArgsConstructor
    public static class MatchInfo {
        private String textPhrase;
        private String function;
        private double similarity;
    }
}
