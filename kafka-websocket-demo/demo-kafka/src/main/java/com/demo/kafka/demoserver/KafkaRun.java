package com.demo.kafka.demoserver;

import com.demo.kafka.demoserver.beans.Message;
import com.demo.kafka.demoserver.provider.KafkaSender;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import javax.ws.rs.core.GenericType;

import java.lang.reflect.Type;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@Component
public class KafkaRun implements CommandLineRunner {

    @Autowired
    private KafkaSender sender;

    @Value("${app.autorun}")
    private boolean autorun;

    @Override
    public void run(String... args) throws Exception {

        if (autorun) {
            for (; ; ) {
                //调用消息发送类中的消息发送方法
                sender.send(null);

                try {
                    Thread.sleep(10000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }

    }
}
