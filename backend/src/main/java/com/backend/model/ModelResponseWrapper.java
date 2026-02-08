package com.backend.model;

import lombok.Data;
import java.util.List;

@Data
public class ModelResponseWrapper {
    private List<ModelResponse> result;
}
