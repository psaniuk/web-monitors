from queue import Queue

from app.background_jobs.web_monitor import WebMonitorTrigger
from app.models import *


class TestWebMonitorTrigger:
    def test_can_start_once(self):
        trigger = self.createMonitorTrigger()
        assert trigger.start()
        assert not trigger.start()

    def test_can_stop_after_start(self):
        trigger = self.createMonitorTrigger()
        assert not trigger.stop()
        trigger.start()
        assert trigger.stop()

    def test_enqueue(self):
        test_queue = Queue()
        trigger = self.createMonitorTrigger(test_queue)
        assert test_queue.qsize() == 0
        trigger.start()
        trigger.stop()
        assert test_queue.qsize() >= 1

    def createMonitorTrigger(self, queue=Queue()):
        config = HttpCheckConfig("https://www.google.com", 200)
        triggerConfig = HttpCheckTrigger(0.1, [config])
        return WebMonitorTrigger(triggerConfig, queue)
