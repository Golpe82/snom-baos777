# start existing system processes in the db
import asyncio
from django.conf import settings

from django.core.management.base import BaseCommand
from knx.models import Subprocess

SYSTEM_SUBPROCESSES = {
    "monitor": "baos777/launch_monitor.py",
    "syslog": "snomsyslogknx/main.py"
    }

class Command(BaseCommand):
    help = "Restart system subprocesses existing in the db (knx monitor or knx syslog)"

    def handle(self, *args, **options):
        try:
            subprocesses = Subprocess.objects.all()
        except Exception:
            self.stdout.write("Exception restarting system subprocesses")

        self._restart_system_subprocesses(subprocesses)

    def _restart_system_subprocesses(self, subprocesses):
        for subprocess in subprocesses:
            if subprocess.name in SYSTEM_SUBPROCESSES.keys():
                path = SYSTEM_SUBPROCESSES.get(subprocess.name)
                absolute_path = f"{str(settings.BASE_DIR.parent)}/{path}"
                subprocess.delete()
                coroutine = self._prepare_system_coroutine(subprocess.name, absolute_path)
                message = self.style.SUCCESS(f"Restarted subprocess {subprocess.name} with PID {subprocess.pid}") 
                asyncio.run(coroutine) 
            else:
                message = self.style.WARNING(f"{subprocess} is not a system process")
            
            self.stdout.write(message) 

    async def _prepare_system_coroutine(self, name, path):
        subprocess = await asyncio.create_subprocess_exec("python3", path)
        await Subprocess.objects.acreate(type="system", name=name, pid=subprocess.pid)
