package com.demo.socket.demosocket.handler;

import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.BoundValueOperations;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.net.InetSocketAddress;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class MyWebSocketServer extends WebSocketServer {

    private final static Logger logger = LoggerFactory.getLogger(MyWebSocketServer.class);

    private final static ConcurrentHashMap<String, WebSocket> webSocketMap = new ConcurrentHashMap<String, WebSocket>(1024);

    private static int port = 8886;

    @Value("${socket.hostinfo}")
    private String hostinfo;

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    public MyWebSocketServer() {
        super(new InetSocketAddress(port));
    }

    @Override
    public void onOpen(WebSocket webSocket, ClientHandshake clientHandshake) {
        logger.info("webSocket服务已建立");
        String userName = clientHandshake.getResourceDescriptor().replace("/","");
        webSocketMap.put(userName, webSocket);
        BoundValueOperations<String, String> valueOps = stringRedisTemplate.boundValueOps(userName);
        valueOps.set(hostinfo);
    }

    @Override
    public void onClose(WebSocket webSocket , int i, String s, boolean b) {
        logger.info("webSocket服务已断开");
        String userName = webSocket.getResourceDescriptor().replace("/","");
        webSocketMap.remove(userName);
        stringRedisTemplate.delete(userName);
    }

    @Override
    public void onMessage(WebSocket webSocket, String s) {
        broadcast("你好新人！");
    }

    @Override
    public void onError(WebSocket webSocket, Exception e) {
        logger.error(e.getMessage());
    }

    @Override
    public void onStart() {
        logger.info("webSocket服务已启动");
    }

    public static ConcurrentHashMap<String, WebSocket> getWebSocketMap() {
        return webSocketMap;
    }
}
