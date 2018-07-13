package com.demo.kafka.demoserver.provider;

import com.demo.kafka.demoserver.beans.Message;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.BoundValueOperations;
import org.springframework.data.redis.core.BoundZSetOperations;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.util.Set;

@Component
public class KafkaSender {

    private final static Logger logger = LoggerFactory.getLogger(KafkaSender.class);

    @Autowired
    private KafkaTemplate kafkaTemplate;

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    private Gson gson = new GsonBuilder().create();

    //发送消息方法
    public void send(Message message) {

        if (message == null) {
            Set<String> keys = stringRedisTemplate.keys("user*");
            message = new Message();
            for (String userName : keys) {
                boolean hasKey = stringRedisTemplate.hasKey(userName);
                if (hasKey) {
                    message.setUserName(userName);
                    message.setMessage("你好：" + userName);

                    BoundValueOperations<String, String> valueOps = stringRedisTemplate.boundValueOps(userName);
                    String topic= valueOps.get();
                    logger.info("+++++++++++++++++++++  topic = {}", gson.toJson(topic));
                    logger.info("+++++++++++++++++++++  message = {}", gson.toJson(message));
                    kafkaTemplate.send(topic, gson.toJson(message));
                }
            }
        }
        else {
            String userName = message.getUserName();
            boolean hasKey = stringRedisTemplate.hasKey(userName);
            if (hasKey) {
                BoundValueOperations<String, String> valueOps = stringRedisTemplate.boundValueOps(userName);
                String topic= valueOps.get();
                logger.info("+++++++++++++++++++++  topic = {}", gson.toJson(topic));
                logger.info("+++++++++++++++++++++  message = {}", gson.toJson(message));
                kafkaTemplate.send(topic, gson.toJson(message));
            }
            else {
                logger.info("没有该用户：{}", userName);
            }
        }


    }
}
