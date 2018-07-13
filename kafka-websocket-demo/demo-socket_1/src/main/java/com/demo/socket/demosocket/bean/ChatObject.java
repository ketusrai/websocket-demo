package com.demo.socket.demosocket.bean;

public class ChatObject {
        private String chatEvent;

        private String userName ;

        private String message;

        public String getChatEvent() {
                return chatEvent;
        }

        public void setChatEvent(String chatEvent) {
                this.chatEvent = chatEvent;
        }

        public String getUserName() {
                return userName;
        }

        public void setUserName(String userName) {
                this.userName = userName;
        }

        public String getMessage() {
                return message;
        }

        public void setMessage(String message) {
                this.message = message;
        }
}
