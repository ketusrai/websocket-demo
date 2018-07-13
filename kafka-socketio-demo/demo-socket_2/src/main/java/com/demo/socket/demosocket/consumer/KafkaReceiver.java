package com.demo.socket.demosocket.consumer;

import com.corundumstudio.socketio.AckRequest;
import com.corundumstudio.socketio.SocketIOClient;
import com.corundumstudio.socketio.SocketIOServer;
import com.corundumstudio.socketio.listener.DataListener;
import com.corundumstudio.socketio.protocol.Packet;
import com.demo.socket.demosocket.bean.ChatObject;
import com.demo.socket.demosocket.bean.Message;
import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.util.JSONPObject;
import com.google.gson.Gson;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.json.GsonJsonParser;
import org.springframework.boot.json.JsonJsonParser;
import org.springframework.data.redis.core.BoundZSetOperations;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.Set;
import java.util.UUID;

@Component
public class KafkaReceiver {

    private final static Logger logger = LoggerFactory.getLogger(KafkaReceiver.class);

    @Autowired
    private SocketIOServer socketIOServer;

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

            boolean hasKey = stringRedisTemplate.hasKey(userName);
            if (hasKey) {
                BoundZSetOperations<String, String> zset = stringRedisTemplate.boundZSetOps(userName);
                String sessionId = zset.range(1, 1).iterator().next();
                SocketIOClient client = socketIOServer.getClient(UUID.fromString(sessionId));
                if (client == null) {
                    stringRedisTemplate.delete(userName);
                }
                client.sendEvent("chatevent",msg);
            }
            else {
                logger.info("没有找到用户：{}的连接信息", userName);
            }

        }

    }
}
