package org.example;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.errors.WakeupException;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Objects;
import java.util.Arrays;
import java.util.Properties;

public class ConsumerGracefulShutdownEx {

    private static final Logger log = LoggerFactory.getLogger(ConsumerGracefulShutdownEx.class.getSimpleName());

    public static void main(String[] args){

        String topic = "demo_java";
        String groupId = "my-java-application";

        Properties properties = new Properties();

        properties.setProperty("bootstrap.servers", "127.0.0.1:29092");

        properties.setProperty("key.deserializer", StringDeserializer.class.getName());
        properties.setProperty("value.deserializer", StringDeserializer.class.getName());
        properties.setProperty("group.id",groupId);
        properties.setProperty("auto.offset.reset", "latest"); //None, earilest, latest 중 선택

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(properties);

        final Thread mainThread = Thread.currentThread();
        Runtime.getRuntime().addShutdownHook(new Thread(){
            @Override
            public void run() {
                log.info("shutdown 감지, consumer.wakeup() 호출");

                // wakeup : 정상적인 종료를 위해 사용
                // record polling 중에 어떤 장애가 발생하더라도 데이터 유실을 막기 위한 안전한 예외 처리
                consumer.wakeup();

                // main thread가 종료한다는 것을 기다림
                try {
                    mainThread.join();
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }

            }
        });

        try {
            consumer.subscribe(Arrays.asList(topic));

            while (true) {

                log.info("polling");
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
                for (ConsumerRecord<String, String> record: records){
                    log.info("Key: " + record.key() + ", Value: " + record.value());
                    log.info("Partition: " + record.partition() + ", Offset: " + record.offset());

                    if (Objects.equals(record.value(), "SHUTDOWN")) {
                        log.info("=== SHUTDOWN ===");
                        throw new WakeupException();
                    }
                }

            }
        } catch (WakeupException e) {
            log.info("Consumer shutdown 시작");
        } catch (Exception e) {
            log.error("Unexpected exception in consumer: ", e);
        } finally {
            consumer.close();
            log.info("consumer: gracefully shut down");
        }




    }

}
