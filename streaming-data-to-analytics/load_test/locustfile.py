# This code will publish messages to the Pub/sub topic to simulate events from other systems
from locust import HttpUser, task, between
import uuid
import time
import random
from random import randrange
from faker import Faker
import os
import json


actions = ["created", "cancelled", "updated", "delivered"]
gcp_token = os.getenv("GCP_TOKEN")
wait_time_interval = os.getenv("WAIT_TIME_INTERVAL")

class IngestAPIUser(HttpUser):
    wait_time = between(0.01,float(wait_time_interval))

    @task()
    def call_ingest_api(self):
        fake = Faker()
        lot_value = randrange(10)
        self.client.headers = {'Authorization': "Bearer " + gcp_token}
        if (lot_value < 9):
            order = {
                "order_id": str(uuid.uuid1()),
                "customer_email": fake.free_email(),
                "phone_number": fake.phone_number(),
                "user_agent": fake.chrome(),
                "action": random.choice(actions),
                "action_time": int(time.time())
            }
            data = json.dumps(order).encode("utf-8")
            self.client.post(f"/?entity=order-event", data=data)
        else:
            error = {
                "user_agent": fake.chrome(),
                "action": random.choice(actions),
                "action_time": int(time.time())
            }
            data = json.dumps(error).encode("utf-8")
            self.client.post(f"/?unknown_event", data=data)
        
