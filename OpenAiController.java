package com.example.demo.controller;

import com.example.demo.dto.AzureCompletionResponse;
import com.example.demo.dto.AzureRequestBody;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class OpenAiController {

    private final WebClient webClient;

    // 从配置文件中读取 Azure OpenAI 的相关配置
    @Value("${azure.openai.url}")
    private String azureOpenAiUrl;

    @Value("${azure.openai.api-key}")
    private String azureApiKey;

    public OpenAiController(WebClient webClient) {
        this.webClient = webClient;
    }
    /**
     * 接口示例： GET /openai?query=你好&stream=false
     * 如果 stream=true 则返回流式数据，返回类型为 Flux<AzureCompletionResponse>，
     * 否则返回单条响应，但为了统一返回类型，这里也包装成 Flux。
     */
    @GetMapping(value = "/openai", produces = MediaType.APPLICATION_NDJSON_VALUE)
    public Flux<AzureCompletionResponse> queryOpenAi(
            @RequestParam("query") String query,
            @RequestParam(name = "stream", defaultValue = "false") boolean stream) {
        // 构造发送给 Azure OpenAI 的请求参数
        AzureRequestBody requestBody = new AzureRequestBody(query, stream);

        Map<String, Object> requestBodyMap = Map.of(
                "stream", requestBody.isStream(),
                "messages", List.of(
                        Map.of(
                                "role", "user",
                                "content", requestBody.getPrompt()
                        )
                )
        );


        // 调用 Azure OpenAI 接口时，需要设置必要的 header，如 api-key、Content-Type 等
        // 注意：这里示例中将请求的返回数据简单当作 String 处理，实际返回结构请参考接口文档
        if (stream) {
            // 流式调用，返回一个 Flux，每一条记录通过 map 封装为 AzureCompletionResponse
            return webClient.post()
                    .uri(azureOpenAiUrl)
                    .header("api-key", azureApiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Mono.just(requestBodyMap), Map.class)
                    .retrieve()
                    .bodyToFlux(String.class)
                    .map(chunk -> new AzureCompletionResponse(chunk));
        } else {
            // 非流式调用，使用 bodyToMono 获取结果，然后包装成 Flux 返回
            return webClient.post()
                    .uri(azureOpenAiUrl)
                    .header("api-key", azureApiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Mono.just(requestBodyMap), Map.class)
                    .retrieve()
                    .bodyToMono(String.class)
                    .map(responseStr -> new AzureCompletionResponse(responseStr))
                    .flux();
        }
    }
}
