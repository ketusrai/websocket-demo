package com.demo.kafka.demoserver;


import java.nio.ByteBuffer;
import java.time.format.DateTimeFormatter;
import java.time.format.FormatStyle;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.LongAdder;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Test {
    public static void main(String[] args) {
        Test test = new Test();
        List<Person> aList = new ArrayList<>();
        aList.add(test.new Person("a", 1));
        aList.add(test.new Person("b", 2));
        aList.add(test.new Person("c", 3));
        aList.stream().map(Person::getName).collect(Collectors.toList());

        aList.stream().collect(Collectors.groupingBy(Person::getAge));

    }

    class Person {
        private String name;
        private Integer age;

        public Person(String name, Integer age) {
            this.name = name;
            this.age = age;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public Integer getAge() {
            return age;
        }

        public void setAge(Integer age) {
            this.age = age;
        }
    }
}
