import typer
import requests
import asyncio
import websockets
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

app = typer.Typer(help="Personal Firewall SOC CLI")
console = Console()

API_BASE = "http://localhost:8000/api/firewall"
WS_BASE = "ws://localhost:8000/ws/alerts"
API_ROOT = "http://localhost:8000"

@app.command()
def status():
    """Check if the SOC Backend API is online."""
    try:
        response = requests.get(f"{API_ROOT}/", timeout=5)
        response.raise_for_status()
        data = response.json()
        console.print(Panel(f"[bold green]Status: {data.get('status', 'online')}[/]\n{data.get('message', 'API is running')}", title="System Status"))
    except Exception as e:
        console.print(f"[bold red]Error:[/] Could not connect to the backend API. Is it running? ({e})")

@app.command()
def list():
    """List all currently blocked IP addresses."""
    try:
        response = requests.get(f"{API_BASE}/blocked")
        response.raise_for_status()
        data = response.json()
        
        if not data:
            console.print("[bold yellow]No active blocks found.[/]")
            return

        table = Table(title="Currently Blocked IPs")
        table.add_column("IP Address", style="cyan", no_wrap=True)
        table.add_column("Threat Score", justify="right", style="magenta")
        table.add_column("Country", style="green")
        table.add_column("Reason", style="yellow")
        table.add_column("In Kernel?", style="blue")

        for b in data:
            table.add_row(
                b.get("ip", "Unknown"),
                str(b.get("threat_score", 0)),
                b.get("country", "Unknown"),
                b.get("reason", ""),
                "Yes" if b.get("in_system") else "No"
            )

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to fetch blocked IPs ({e})")

@app.command()
def block(ip: str, reason: str = typer.Option("Manual Action via SOC CLI", "--reason", "-r", help="Reason for blocking")):
    """Manually block an IP address."""
    try:
        payload = {"ip_address": ip, "reason": reason}
        response = requests.post(f"{API_BASE}/block", json=payload)
        response.raise_for_status()
        data = response.json()
        intel = data.get("threat_intel", {})
        console.print(f"[bold green]Success![/] Successfully blocked {ip}")
        if intel:
            console.print(f"AbuseIPDB Threat Score: {intel.get('threat_score')} | Country: {intel.get('country_code')}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to block {ip} ({e})")

@app.command()
def unblock(ip: str):
    """Manually unblock an IP address."""
    try:
        payload = {"ip_address": ip, "reason": "Unblocked via SOC CLI"}
        response = requests.post(f"{API_BASE}/unblock", json=payload)
        response.raise_for_status()
        console.print(f"[bold green]Success![/] Successfully unblocked {ip}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to unblock {ip} ({e})")

@app.command()
def threat(ip: str):
    """Check the threat intelligence score for an IP."""
    try:
        response = requests.get(f"{API_BASE}/threat/{ip}")
        response.raise_for_status()
        data = response.json()
        
        score = data.get('threat_score', 0)
        color = "red" if score > 50 else ("yellow" if score > 20 else "green")
        
        console.print(Panel(
            f"IP: [cyan]{ip}[/]\n"
            f"Score: [bold {color}]{score}[/]\n"
            f"Country: [green]{data.get('country_code', 'Unknown')}[/]",
            title="Threat Intelligence"
        ))
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to fetch threat intelligence ({e})")

async def _stream_alerts():
    try:
        console.print(f"[bold cyan]Connecting to {WS_BASE}...[/]")
        async with websockets.connect(WS_BASE) as websocket:
            console.print("[bold green]Connected! Listening for live alerts... (Press Ctrl+C to stop)[/]")
            while True:
                message = await websocket.recv()
                try:
                    alert = json.loads(message)
                    source = alert.get("source", "UNKNOWN")
                    
                    if source == "suricata":
                        console.print(f"[[bold red]SURICATA[/]] {alert.get('alert_type', '')} from {alert.get('src_ip')} -> {alert.get('dest_ip')}")
                    elif source == "wazuh":
                        console.print(f"[[bold blue]WAZUH[/]] {alert.get('description', '')} on {alert.get('agent_name')} (Level {alert.get('rule_level')})")
                    else:
                        console.print(f"[raw alert] {message}")
                except json.JSONDecodeError:
                    console.print(f"[Raw message] {message}")
    except websockets.exceptions.ConnectionClosed:
        console.print("[bold yellow]Connection closed by server.[/]")
    except Exception as e:
        console.print(f"[bold red]WebSocket Error:[/] {e}")

@app.command()
def monitor():
    """Stream live Suricata and Wazuh alerts to the terminal."""
    try:
        asyncio.run(_stream_alerts())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Monitoring stopped.[/]")

if __name__ == "__main__":
    app()
