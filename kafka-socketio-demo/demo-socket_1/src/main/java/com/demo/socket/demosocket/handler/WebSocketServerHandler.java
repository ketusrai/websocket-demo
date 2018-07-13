package com.demo.socket.demosocket.handler;

import com.corundumstudio.socketio.*;
import com.corundumstudio.socketio.listener.ConnectListener;
import com.corundumstudio.socketio.listener.DataListener;
import com.corundumstudio.socketio.listener.DisconnectListener;
import com.corundumstudio.socketio.protocol.Packet;
import com.demo.socket.demosocket.bean.ChatObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.BoundZSetOperations;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.UUID;


@Service
public class WebSocketServerHandler {

    private final static Logger logger = LoggerFactory.getLogger(WebSocketServerHandler.class);

    @Value("${socket.hostinfo}")
    private String hostInfo;

    @Autowired
    private SocketIOServer socketIOServer;

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    public void run() {
        socketIOServer.addConnectListener(new ConnectListener() {
            @Override
            public void onConnect(SocketIOClient socketIOClient) {
                String userName = (String)socketIOClient.getHandshakeData().getUrlParams().get("userName").get(0);
                UUID sessionId = socketIOClient.getSessionId();
                boolean hasKey = stringRedisTemplate.hasKey(userName);
                if (hasKey) {
                    stringRedisTemplate.delete(userName);
                }
                BoundZSetOperations<String, String> zset = stringRedisTemplate.boundZSetOps(userName);
                zset.add(hostInfo, 0);
                zset.add(sessionId.toString(), 1);
                System.out.println(userName);

            }
        });
        socketIOServer.addDisconnectListener(new DisconnectListener(){
            @Override
            public void onDisconnect(SocketIOClient socketIOClient) {
                String userName = (String)socketIOClient.getHandshakeData().getUrlParams().get("userName").get(0);
                boolean hasKey = stringRedisTemplate.hasKey(userName);
                if (hasKey) {
                    stringRedisTemplate.delete(userName);
                }
                System.out.println(userName);
            }
        });
        socketIOServer.start();

        logger.info("webSocket服务已启动");

        //testService.test();
        socketIOServer.addEventListener("chatevent", ChatObject.class, new DataListener<ChatObject>() {
            @Override
            public void onData(SocketIOClient client, ChatObject data, AckRequest ackRequest) {
                // broadcast messages to all clients
                System.out.println(data.toString());
                socketIOServer.getBroadcastOperations().sendEvent("chatevent", data);
            }
        });
    }


}
