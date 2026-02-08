package com.backend.controller;

import com.backend.model.AggregatedResult;
import com.backend.service.ModelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class QueryController {

    @Autowired
    private ModelService modelService;

    @PostMapping("/query")
    public List<AggregatedResult> handleQuery(@RequestBody Map<String, String> payload) {
        String text = payload.get("text");
        if (text == null || text.isEmpty()) {
            System.out.println("[ERROR]: empty text");
            return List.of();
        }

        List<AggregatedResult> result = modelService.sendToModelAndAggregate(text);
        System.out.println("Model response: " + result);

        return result;
    }
}
