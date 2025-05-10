from django.core.management.base import BaseCommand
from background_task.models import Task
from background_task.tasks import tasks
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process background tasks'

    def handle(self, *args, **options):
        self.stdout.write('Starting background task processor...')
        logger.info('Background task processor started')
        
        while True:
            try:
                tasks.run_next_task()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing background task: {str(e)}")
                time.sleep(5)  # Wait longer on error 