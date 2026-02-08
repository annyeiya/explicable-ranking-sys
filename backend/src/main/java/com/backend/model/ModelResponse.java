package com.backend.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class ModelResponse {
    private String org;
    @JsonProperty("text_phrase")
    private String textPhrase;
    private String function;
    private double similarity;
    @JsonProperty("context_boost")
    private double contextBoost;
}
