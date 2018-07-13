package com.demo.kafka.demoserver.controller;

import com.demo.kafka.demoserver.beans.Message;
import com.demo.kafka.demoserver.provider.KafkaSender;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ClientController {

//    @Autowired
//    private KafkaSender sender;

    @RequestMapping(value = "/hi")
    public String sayHi(@RequestBody Message message) {
        //sender.send(message);
        return "SUCCESS";
    }

}
