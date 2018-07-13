package com.demo.socket.demosocket.consumer;

import com.demo.socket.demosocket.bean.Message;
import com.demo.socket.demosocket.handler.MyWebSocketServer;
import com.google.gson.Gson;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.java_websocket.WebSocket;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class KafkaReceiver {

    private final static Logger logger = LoggerFactory.getLogger(KafkaReceiver.class);

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    @KafkaListener(topics = {"${socket.hostinfo}"})
    public void listen(ConsumerRecord<?, ?> record) {

        Optional<?> kafkaMessage = Optional.ofNullable(record.value());

        if (kafkaMessage.isPresent()) {
            Object message = kafkaMessage.get();
            logger.info("kafka消费端消息接受开始");
            logger.info("----------------- record =" + record);
            logger.info("------------------ message =" + message);
            logger.info("我要把消息推送给websocket");

            Gson gs  =new Gson();
            Message msg = gs.fromJson(message.toString(),Message.class);
            String userName = msg.getUserName();

            ConcurrentHashMap<String, WebSocket> webSocketMap = MyWebSocketServer.getWebSocketMap();
            WebSocket webSocket = webSocketMap.get(userName);
            if (webSocket != null) {
                webSocket.send(message.toString());
            }
            else {
                logger.info("没有找到用户：{}的连接信息", userName);
            }
        }

    }
}
