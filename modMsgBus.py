#!/usr/bin/python
import sys
import os
import pika

class rabbitmqListener:
    def processMessage(self, ch, method, properties, body):
        message = body.decode("utf-8")
        print(message)

    def ingestMessages(self):
        self.msgBusConnection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.msgBusChannel = self.msgBusConnection.channel()
        self.msgBusChannel.queue_declare(queue='mainComm')
        self.msgBusChannel.basic_consume(queue='mainComm', on_message_callback=self.processMessage, auto_ack=True)
        self.msgBusChannel.start_consuming()

    def __init__(self):
        rabbitMQStopped = os.system("service rabbitmq-server status > /dev/null 2>&1")
        if rabbitMQStopped:
            try:
                os.system("service rabbitmq-server start > /dev/null 2>&1")
            except Exception as e:
                print("Couldn't start RabbitMQ server, shutting down...")
                print(e)
                sys.exit()
        
msgBus = rabbitmqListener()
msgBus.ingestMessages()