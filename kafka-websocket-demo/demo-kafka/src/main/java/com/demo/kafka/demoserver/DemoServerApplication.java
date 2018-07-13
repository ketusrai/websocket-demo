package com.demo.kafka.demoserver;

import com.demo.kafka.demoserver.beans.MessageConverter;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

import java.util.List;

@SpringBootApplication
public class DemoServerApplication extends WebMvcConfigurerAdapter {

    public static void main(String[] args) {

        SpringApplication.run(DemoServerApplication.class, args);
    }

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        super.configureMessageConverters(converters);
        converters.add(new MessageConverter());
    }

}
