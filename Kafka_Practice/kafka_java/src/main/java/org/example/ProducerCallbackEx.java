package org.example;

import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;

public class ProducerCallbackEx {

    private static final Logger log = LoggerFactory.getLogger(ProducerCallbackEx.class.getCanonicalName());

    public static void main(String[] args){

        // 1. property 세팅
        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "127.0.0.1:29092");

        properties.setProperty("key.serializer", StringSerializer.class.getName());
        properties.setProperty("value.serializer",StringSerializer.class.getName());
        properties.setProperty("partitioner.class", RoundRobinPartitioner.class.getName());

        // 2. producer 생성
        KafkaProducer<String, String> producer = new KafkaProducer<>(properties);

        // 3. record를 producer에 전송

        for (int i = 0; i < 30; i++){
            ProducerRecord<String, String> producerRecord = new ProducerRecord<>("demo_java2", "fastcampus " + i);
            producer.send(producerRecord, new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {

                    if (exception == null) {
                        log.info("metadata ==> \n" +
                                "topic : " + metadata.topic() + "\n" +
                                "Partition : " + metadata.partition() +"\n" +
                                "Offset : " + metadata.offset() + "\n" +
                                "Timestamp : " + metadata.timestamp());
                    } else{
                        log.error("Error while producing", exception);
                    }
                }
            });

            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        // 전부 partition1로 들어옴
        // Round robin을 지정해주면 골고루 들어감(sleep 지정안해주면 하나에 다 들어감)

        // 4. producer 종료
        producer.close();


    }
}

