import logging
import signal
from os import environ

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from generator.generator import Generator


class Daemon:
    logger = logging.getLogger(__name__)

    @classmethod
    def prepare_scheduler(
        cls, cron_key_change: str, cron_queue_upload: str
    ) -> BaseScheduler:
        cls.logger.debug("Using BlockingScheduler")
        scheduler = BlockingScheduler()
        cls.logger.debug(f"Scheduling Key Rotation: {cron_key_change}")
        schedule_key_change = CronTrigger.from_crontab(cron_key_change)
        cls.logger.debug(f"Scheduling Queue upload: {cron_queue_upload}")
        schedule_queue_upload = CronTrigger.from_crontab(cron_queue_upload)

        scheduler.add_job(Generator.change_key, schedule_key_change)
        scheduler.add_job(Generator.upload_queue_to_kms, schedule_queue_upload)

        # In order to shutdown clean, capture system signals
        # and shut down the scheduler.
        def graceful_shutdown(signum, frame) -> None:
            scheduler.shutdown()

        signal.signal(signal.SIGINT, graceful_shutdown)
        signal.signal(signal.SIGTERM, graceful_shutdown)
        return scheduler

    @classmethod
    def run(cls) -> None:
        cron_key_change = environ.get("SCHEDULE_GENERATE", "0 * * * *")
        cron_queue = environ.get("SCHEDULE_QUEUE", "*/5 * * * *")
        scheduler = Daemon.prepare_scheduler(cron_key_change, cron_queue)
        cls.logger.info("Starting daemon")
        scheduler.start()
        cls.logger.info("Stopping daemon")
