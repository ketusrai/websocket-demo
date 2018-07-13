package com.demo.socket.demosocket.runner;

import com.corundumstudio.socketio.*;
import com.corundumstudio.socketio.protocol.Packet;
import com.demo.socket.demosocket.handler.WebSocketServerHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.net.SocketAddress;
import java.util.Set;
import java.util.UUID;

@Component
public class ServerRunner implements CommandLineRunner {

    @Autowired
    private WebSocketServerHandler handler;


    @Override
    public void run(String... strings) throws Exception {
        handler.run();
    }
}
