import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

CACHE_FILE = Path(__file__).parent / "pricing_cache.json"

def load_data():
    if not CACHE_FILE.exists():
        return None
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def main():
    console = Console()
    
    data = load_data()
    if not data:
        console.print("[bold red]Error:[/] No se encontró el archivo de caché o está corrupto.")
        console.print("Por favor, ejecuta [bold cyan]python scraperv2.py[/] primero para generar los datos.")
        return

    # Título principal
    console.print(Panel.fit(
        "[bold cyan]QSimplify[/] - Reporte de Costos de Hardware Cuántico", 
        border_style="cyan"
    ))
    
    inner_data = data.get("data", {})
    last_update = inner_data.get("generated_at", "Desconocida")
    console.print(f"[dim]Última actualización: {last_update}[/]\n")

    providers = inner_data.get("providers", {})

    # ==========================================
    # Tabla de AWS Braket
    # ==========================================
    aws_data = providers.get("aws_braket", {})
    if aws_data.get("status") == "success":
        aws_table = Table(title="[bold orange3]Precios de AWS Braket (On-Demand)[/]", show_header=True, header_style="bold orange3")
        aws_table.add_column("Proveedor", style="cyan", no_wrap=True)
        aws_table.add_column("Familia QPU", style="magenta")
        aws_table.add_column("Precio por Tarea (USD)", justify="right", style="green")
        aws_table.add_column("Precio por Shot (USD)", justify="right", style="green")

        qpu_prices = aws_data.get("data", {}).get("qpu_prices", [])
        for item in qpu_prices:
            provider_name = item.get("hardware_provider", "-")
            family = item.get("qpu_family", "-")
            
            # Formatear a 5 decimales si es posible, sino mostrar guión
            per_task = item.get("per_task_usd")
            per_task_str = f"${per_task:.5f}" if per_task is not None else "-"
            
            per_shot = item.get("per_shot_usd")
            per_shot_str = f"${per_shot:.6f}" if per_shot is not None else "-"

            aws_table.add_row(provider_name, family, per_task_str, per_shot_str)
        
        console.print(aws_table)
        console.print()
    else:
        console.print("[red]No se pudieron cargar los datos de AWS Braket.[/]")

    # ==========================================
    # Tabla de IBM Quantum
    # ==========================================
    ibm_data = providers.get("ibm_quantum", {})
    if ibm_data.get("status") == "success":
        ibm_table = Table(title="[bold blue]Precios de IBM Quantum[/]", show_header=True, header_style="bold blue")
        ibm_table.add_column("Plan", style="cyan", no_wrap=True)
        ibm_table.add_column("Precio por Segundo (USD)", justify="right", style="green")
        ibm_table.add_column("Precio por Minuto (USD)", justify="right", style="green")
        ibm_table.add_column("Detalle original", style="magenta")

        plans = ibm_data.get("data", {}).get("plans", [])
        
        if plans:
            for plan_info in plans:
                plan_name = plan_info.get("plan", "-")
                
                per_sec = plan_info.get("price_usd_per_second")
                per_sec_str = f"${per_sec:.2f}" if per_sec is not None else "-"
                
                per_min = plan_info.get("price_usd_per_minute")
                per_min_str = f"${per_min:.2f}" if per_min is not None else "-"
                
                label = plan_info.get("price_label", "-")
                
                ibm_table.add_row(plan_name, per_sec_str, per_min_str, label)
            console.print(ibm_table)
        else:
            console.print("[yellow]No se encontraron planes públicos de IBM en el caché.[/]")
            
        console.print()
    else:
        console.print("[red]No se pudieron cargar los datos de IBM Quantum.[/]")

if __name__ == "__main__":
    main()
