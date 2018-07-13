package com.demo.socket.demosocket.runner;

import com.demo.socket.demosocket.handler.MyWebSocketServer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class ServerRunner implements CommandLineRunner {

    @Value("${socket.port}")
    private int port;

    @Autowired
    private MyWebSocketServer server;

    @Override
    public void run(String... strings) throws Exception {
        server.start();
    }
}
