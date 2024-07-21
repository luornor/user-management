from __future__ import absolute_import, unicode_literals

from celery import shared_task
from users.celery import app


@shared_task
def publish_message(message, exchange_name, routing_key):
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish(
            message,
            exchange=exchange_name,
            routing_key=routing_key,
        )


@shared_task
def create_shop(user_data):
    publish_message(user_data, 'listing_exchange', 'shop.created')