package com.demo.socket.demosocket;

import com.demo.socket.demosocket.handler.WebSocketServerHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoSocketApplication {

    @Autowired
    WebSocketServerHandler handler;

    public static void main(String[] args) {
        SpringApplication.run(DemoSocketApplication.class, args);
    }
}
