import sqlite3
import os
from radar.config import DATABASE_PATH
from rich.console import Console
from rich.table import Table

console = Console()

def get_connection():
    if not os.path.exists(DATABASE_PATH):
        console.print(f"[red]Database not found at {DATABASE_PATH}[/red]")
        exit(1)
    return sqlite3.connect(DATABASE_PATH)

def analyze_users():
    conn = get_connection()
    cursor = conn.cursor()

    console.print(f"\n[bold cyan]📊 SonarPro User Funnel Analysis[/bold cyan]")
    console.print(f"Database: [dim]{DATABASE_PATH}[/dim]\n")

    # 1. Total Users (Registered/Active)
    # We infer registration by presence in any user-centric table since auth is external (Clerk)
    query_total = """
    SELECT COUNT(DISTINCT user_id) 
    FROM (
        SELECT user_id FROM products
        UNION
        SELECT user_id FROM user_settings
        UNION
        SELECT user_id FROM sync_runs
    )
    """
    cursor.execute(query_total)
    total_users = cursor.fetchone()[0]

    # 2. Users who created a product
    query_products = "SELECT COUNT(DISTINCT user_id) FROM products"
    cursor.execute(query_products)
    with_products = cursor.fetchone()[0]

    # 3. Users with Product + Ran Analysis (Sync)
    query_analysis = """
    SELECT COUNT(DISTINCT p.user_id) 
    FROM products p
    JOIN sync_runs s ON p.user_id = s.user_id
    """
    cursor.execute(query_analysis)
    with_analysis = cursor.fetchone()[0]

    # 4. Users with Analysis + AI Response/Interaction
    # We count 'generated_responses' as AI usage
    # We count 'triage_history' as interaction (closest proxy to 'clicking/using' threads)
    query_power_users = """
    SELECT COUNT(DISTINCT p.user_id) 
    FROM products p
    JOIN sync_runs s ON p.user_id = s.user_id
    WHERE p.user_id IN (
        SELECT user_id FROM generated_responses
        UNION
        SELECT user_id FROM triage_history
    )
    """
    cursor.execute(query_power_users)
    power_users = cursor.fetchone()[0]

    # Display Results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim")
    table.add_column("Count", justify="right")
    table.add_column("Conversion", justify="right")

    table.add_row("1. Total Users (Active)", str(total_users), "100%")
    
    conv_prod = f"{(with_products/total_users*100):.1f}%" if total_users else "0%"
    table.add_row("2. Created Product", str(with_products), conv_prod)
    
    conv_ana = f"{(with_analysis/with_products*100):.1f}%" if with_products else "0%"
    table.add_row("3. Ran Analysis", str(with_analysis), conv_ana)
    
    conv_power = f"{(power_users/with_analysis*100):.1f}%" if with_analysis else "0%"
    table.add_row("4. Power Users (AI/Triage)", str(power_users), conv_power)

    console.print(table)

    # --- LIST IDs ---
    console.print("\n[bold cyan]📋 User IDs by Category[/bold cyan]")
    
    cursor.execute("""
        SELECT DISTINCT user_id FROM products 
        UNION SELECT user_id FROM user_settings 
        UNION SELECT user_id FROM sync_runs
    """)
    all_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT user_id FROM products")
    prod_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT p.user_id FROM products p JOIN sync_runs s ON p.user_id = s.user_id")
    ana_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT p.user_id FROM products p JOIN sync_runs s ON p.user_id = s.user_id
        WHERE p.user_id IN (SELECT user_id FROM generated_responses UNION SELECT user_id FROM triage_history)
    """)
    power_ids = [r[0] for r in cursor.fetchall()]

    console.print(f"\n[yellow]1. All Active IDs ({len(all_ids)}):[/yellow]")
    console.print(", ".join(all_ids))

    console.print(f"\n[yellow]2. Created Product ({len(prod_ids)}):[/yellow]")
    console.print(", ".join(prod_ids))

    console.print(f"\n[yellow]3. Ran Analysis ({len(ana_ids)}):[/yellow]")
    console.print(", ".join(ana_ids))

    console.print(f"\n[yellow]4. Power Users ({len(power_ids)}):[/yellow]")
    console.print(", ".join(power_ids) if power_ids else "None")

    console.print("\n[dim]Note: Copy these IDs and check them in your Clerk Dashboard to see emails.[/dim]")
    conn.close()

if __name__ == "__main__":
    analyze_users()
