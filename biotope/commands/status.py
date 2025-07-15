"""Status command implementation using Git under the hood."""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
from rich.console import Console
from rich.table import Table


@click.command()
@click.option(
    "--porcelain",
    is_flag=True,
    help="Output in machine-readable format",
)
@click.option(
    "--biotope-only",
    is_flag=True,
    help="Show only .biotope/ directory changes",
)
def status(porcelain: bool, biotope_only: bool) -> None:
    """
    Show the current status of the biotope project using Git.
    
    Displays Git status for .biotope/ directory changes.
    Similar to git status but focused on metadata.
    
    Args:
        porcelain: Output in machine-readable format
        biotope_only: Show only .biotope/ directory changes
    """
    console = Console()
    
    # Find biotope project root
    biotope_root = find_biotope_root()
    if not biotope_root:
        click.echo("❌ Not in a biotope project. Run 'biotope init' first.")
        raise click.Abort

    # Check if we're in a Git repository
    if not _is_git_repo(biotope_root):
        click.echo("❌ Not in a Git repository. Initialize Git first with 'git init'.")
        raise click.Abort

    if porcelain:
        _show_porcelain_status(biotope_root, biotope_only)
    else:
        _show_rich_status(biotope_root, console, biotope_only)


def _show_rich_status(biotope_root: Path, console: Console, biotope_only: bool) -> None:
    """Show status with rich formatting."""
    
    # Get Git status
    git_status = _get_git_status(biotope_root, biotope_only)
    
    console.print(f"\n[bold blue]Biotope Project Status[/]")
    console.print(f"Project: {biotope_root.name}")
    console.print(f"Location: {biotope_root}")
    console.print(f"Git Repository: {'✅' if _is_git_repo(biotope_root) else '❌'}")
    
    # Show changes
    if git_status["staged"]:
        console.print(f"\n[bold green]Changes to be committed:[/]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Status", style="cyan")
        table.add_column("File", style="green")
        
        for status, file_path in git_status["staged"]:
            table.add_row(status, file_path)
        console.print(table)
    
    if git_status["modified"]:
        console.print(f"\n[bold yellow]Changes not staged for commit:[/]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Status", style="cyan")
        table.add_column("File", style="green")
        
        for status, file_path in git_status["modified"]:
            table.add_row(status, file_path)
        console.print(table)
    
    if git_status["untracked"]:
        console.print(f"\n[bold red]Untracked files:[/]")
        for file_path in git_status["untracked"]:
            console.print(f"  ? {file_path}")
    
    # Summary
    total_staged = len(git_status["staged"])
    total_modified = len(git_status["modified"])
    total_untracked = len(git_status["untracked"])
    
    console.print(f"\n[bold]Summary:[/]")
    console.print(f"  Staged: {total_staged} file(s)")
    console.print(f"  Modified: {total_modified} file(s)")
    console.print(f"  Untracked: {total_untracked} file(s)")
    
    if total_staged > 0:
        console.print(f"\n💡 Next steps:")
        console.print(f"  • Run 'biotope commit -m \"message\"' to commit changes")
    elif total_modified > 0 or total_untracked > 0:
        console.print(f"\n💡 Next steps:")
        console.print(f"  • Run 'biotope add <data_file>' to add data files")
        console.print(f"  • Run 'biotope annotate interactive --staged' to create metadata")
        console.print(f"  • Run 'biotope commit -m \"message\"' to commit changes")


def _show_porcelain_status(biotope_root: Path, biotope_only: bool) -> None:
    """Show status in machine-readable format."""
    git_status = _get_git_status(biotope_root, biotope_only)
    
    for status, file_path in git_status["staged"]:
        click.echo(f"{status} {file_path}")
    
    for status, file_path in git_status["modified"]:
        click.echo(f"{status} {file_path}")
    
    for file_path in git_status["untracked"]:
        click.echo(f"?? {file_path}")


def _get_git_status(biotope_root: Path, biotope_only: bool) -> Dict[str, List]:
    """Get Git status for .biotope/ directory."""
    try:
        # Get Git status
        cmd = ["git", "status", "--porcelain"]
        if biotope_only:
            cmd.append(".biotope/")
        
        result = subprocess.run(
            cmd,
            cwd=biotope_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        staged = []
        modified = []
        untracked = []
        
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            
            # Parse Git status line (e.g., "M  .biotope/datasets/file.jsonld")
            status = line[:2].strip()
            file_path = line[3:]
            
            if status == "??":
                untracked.append(file_path)
            elif status in ["A", "M", "D", "R"]:
                staged.append((status, file_path))
            elif status in [" M", " D", " R"]:
                modified.append((status.strip(), file_path))
        
        return {
            "staged": staged,
            "modified": modified,
            "untracked": untracked
        }
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Git error: {e}")
        return {"staged": [], "modified": [], "untracked": []}


def _is_git_repo(directory: Path) -> bool:
    """Check if directory is a Git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def find_biotope_root() -> Optional[Path]:
    """Find the biotope project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".biotope").exists():
            return current
        current = current.parent
    return None 