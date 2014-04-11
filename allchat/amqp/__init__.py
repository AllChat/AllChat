import allchat
from allchat.amqp import Impl_kombu as rabbitmq

def init_amqp():
    rabbitmq.get_connection()
    rabbitmq.get_exchange()
