package com.demo.kafka.demoserver.beans;

import org.springframework.http.HttpOutputMessage;
import org.springframework.http.converter.HttpMessageNotWritableException;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;

import java.io.IOException;
import java.lang.reflect.Type;
import java.util.Map;

public class MessageConverter extends MappingJackson2HttpMessageConverter {

    @Override
    protected void writeInternal(Object object, Type type, HttpOutputMessage outputMessage) throws IOException, HttpMessageNotWritableException {

        if (object instanceof Map) {
            Integer status = (Integer) ((Map) object).get("status");
            if (status != null && status % 100 > 3) {
                throw new IOException("未知错误");
            }
        }

        Result result = new Result(object);
        result.setCode(1);
        result.setMessage("test");
        super.writeInternal(result, type, outputMessage);
        System.out.println("it's work");
    }

    class Result {

        private int code;

        private String message;

        private Object result;

        public Result(Object result) {
            this.result = result;
        }

        public int getCode() {
            return code;
        }

        public void setCode(int code) {
            this.code = code;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        public Object getResult() {
            return result;
        }
    }
}
