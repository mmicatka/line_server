from locust import HttpLocust, TaskSet, task
import random

class UserBehavior(TaskSet):
    @task(1)
    def line(l):
        line_index = random.randint(1, 100000000)
        l.client.get('/lines/' + str(line_index), name='/lines/<line_index>')


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 5000
