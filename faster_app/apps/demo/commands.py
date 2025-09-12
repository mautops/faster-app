from rich.console import Console
from faster_app.commands.base import BaseCommand

console = Console()


class PrefixDemoSuffix(BaseCommand):
    """demo command"""

    class Meta:
        PREFIXES = ["Prefix"]
        SUFFIXES = ["Suffix"]

    def run(self):
        """run command description"""
        console.print("[bold green][i]Demo Command[/i]: Hello, World![/bold green]")
