import time
from faster_app.commands.base import CommandBase
from rich.console import Console
from rich.progress import track

console = Console()


class DemoCommand(CommandBase):
    """Demo App Commands"""

    async def run(self):
        console.print("[i]Hello[/i] ABC", style="bold green")
        for step in track(range(50)):
            time.sleep(0.1)
            console.print(f"[progress.description]{step}[/progress.description]")
