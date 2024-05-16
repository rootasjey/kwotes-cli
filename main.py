import json
import requests
import typer

from rich.console import Console
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table, Row
from rich.padding import Padding
from rich.style import Style

app = typer.Typer(no_args_is_help=True)
console = Console()

KWOTES_API_KEY = ""

@app.command()
def recent():
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        expand=True,
    ) as progress:
        progress.add_task(description="Fetching most recent quotes...", total=None, visible=True)

        url = "https://us-central1-memorare-98eee.cloudfunctions.net/api/v1/quotes"
        headers = {"Accept": "application/json", "Authorization": KWOTES_API_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            jsonData = json.loads(response.text)
            data = jsonData["response"]
            quotesData = data["quotes"]

            table = Table(title="Recent Quotes", padding=(0, 1), border_style=Style(), show_lines=False)

            table.add_column("ID", justify="left", style=Style(color="cyan", bold=True), no_wrap=True)
            table.add_column("Name", style=Style(color="magenta", bold=False))
            table.add_column("Author", style="green")
            table.add_column("Reference", style="blue")

            for quoteData in quotesData:
                table.add_row(quoteData["id"], quoteData["name"], quoteData["author"]["name"], quoteData["reference"]["name"], end_section=False)
            
            console.print(table)
        else:
            print(f'Request failed with status code {response.status_code}')


@app.command()
def search(name: str = typer.Argument(help="keyword to search for", default=""), page: int = 0, limit: int = 12):
    if not name:
        name = typer.prompt("Please enter a name to search for: ")
    
    current_batch_count = (page + 1) * limit

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        expand=True,
    ) as progress:
        progress.add_task(description=f"Searching quotes with [bold green] \"{name}\" [/bold green]...", total=None, visible=True)

        url = f"https://us-central1-memorare-98eee.cloudfunctions.net/api/v1/search/quotes?q={name}&page={page}&limit={limit}"
        headers = {"Accept": "application/json", "Authorization": KWOTES_API_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            jsonData = json.loads(response.text)
            # console.print(jsonData)
            data = jsonData["response"]
            quotesData = data["hits"]
            nb_hits = int(data["nbHits"])
            total_page = int(data["nbPages"])
            current_page = int(data["page"])
            current_batch_count = (current_page + 1) * limit

            table = Table(title=f"Search Quotes with \"{name}\" (count: {nb_hits})", padding=(0, 1), border_style=Style(), show_lines=False)

            table.add_column("ID", justify="left", style=Style(color="cyan", bold=True), no_wrap=True)
            table.add_column("Name", style=Style(color="magenta", bold=False))
            table.add_column("Author", style="green")
            table.add_column("Reference", style="blue")

            for quoteData in quotesData:
                table.add_row(quoteData["objectID"], quoteData["name"], quoteData["author"]["name"], quoteData["reference"]["name"], end_section=False)
            
            console.print(table)

            if nb_hits > current_batch_count:
                console.print(Padding(f"Showing {current_batch_count} of {nb_hits} results (page {current_page + 1} of {total_page})", (0, 1, 0, 1)))
            else:
                console.print(Padding(f"Showing last {len(quotesData)} results (page {current_page + 1} of {total_page})", (0, 1, 0, 1)))

            console.print(Padding(f"To see more or less results, use the --page and --limit flag (default: --page 0 --limit 12)", (0, 1, 0, 1)))
        else:
          print(f'Request failed with status code {response.status_code}')

    if current_batch_count < nb_hits:
        show_next = typer.confirm("Show next results?", default=True)

        if show_next:
            search(name, page + 1, limit)

if __name__ == "__main__":
    app()