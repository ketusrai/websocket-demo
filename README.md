# websocket-demo
# 说明
──────────────────────────────
1. 配置文件 (例如 application.properties) 中需配置 Azure OpenAI 的请求地址和 API KEY，例如：
  
  azure.openai.url=https://你的资源名称.openai.azure.com/openai/deployments/你的部署ID/completions?api-version=2023-03-15-preview
  azure.openai.api-key=你的APIKEY

2. 此示例中接口使用 GET 方法，接收 query 与 stream 两个请求参数，你也可以根据需要改成 POST 方法，并把 query 放到 JSON 请求体中；
3. 返回类型统一为 Flux<AzureCompletionResponse>（非 Object 类型），当非流式调用时，仅返回一个元素的 Flux；
4. 本示例中假设 Azure 接口返回的数据为 String 类型（例如一行文本），实际产品中可能需要根据返回的 JSON 结构进行反序列化，建议创建相应 POJO；
5. 如果希望针对流式场景设置 HTTP 返回的 Content-Type 为 text/event-stream，可调整 @GetMapping 的 produces 属性，例如：
     produces = MediaType.TEXT_EVENT_STREAM_VALUE
   但注意非流式时浏览器解析可能有所不同，可根据实际业务区分；
