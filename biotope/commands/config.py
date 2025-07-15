"""Configuration management commands for biotope."""

import yaml
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from biotope.validation import load_biotope_config


@click.group()
def config() -> None:
    """Manage biotope project configuration."""


@config.command()
@click.option(
    "--field",
    "-f",
    help="Field name to add to required fields",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(["string", "object", "array"]),
    help="Data type for the field",
)
@click.option(
    "--min-length",
    type=int,
    help="Minimum length for string/array fields",
)
@click.option(
    "--required-keys",
    help="Comma-separated list of required keys for object fields",
)
def set_validation(field: Optional[str], type: Optional[str], min_length: Optional[int], required_keys: Optional[str]) -> None:
    """Set annotation validation requirements."""
    console = Console()
    
    # Find biotope project root
    biotope_root = _find_biotope_root()
    if not biotope_root:
        click.echo("❌ Not in a biotope project. Run 'biotope init' first.")
        raise click.Abort
    
    config_path = biotope_root / ".biotope" / "config" / "biotope.yaml"
    if not config_path.exists():
        click.echo("❌ Biotope configuration not found. Run 'biotope init' first.")
        raise click.Abort
    
    # Load current config
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        click.echo(f"❌ Error reading configuration: {e}")
        raise click.Abort
    
    # Initialize annotation_validation if it doesn't exist
    if "annotation_validation" not in config:
        config["annotation_validation"] = {
            "enabled": True,
            "minimum_required_fields": [],
            "field_validation": {}
        }
    
    # Add field to required fields
    if field:
        if field not in config["annotation_validation"]["minimum_required_fields"]:
            config["annotation_validation"]["minimum_required_fields"].append(field)
            console.print(f"✅ Added '{field}' to required fields")
        else:
            console.print(f"⚠️  Field '{field}' is already required")
    
    # Add field validation rules
    if field and type:
        field_validation = config["annotation_validation"]["field_validation"]
        field_validation[field] = {"type": type}
        
        if min_length is not None:
            field_validation[field]["min_length"] = min_length
        
        if required_keys:
            keys_list = [key.strip() for key in required_keys.split(",")]
            field_validation[field]["required_keys"] = keys_list
        
        console.print(f"✅ Added validation rules for '{field}'")
    
    # Save updated config
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        console.print("✅ Configuration updated successfully")
    except yaml.YAMLError as e:
        click.echo(f"❌ Error writing configuration: {e}")
        raise click.Abort


@config.command()
def show_validation() -> None:
    """Show current annotation validation requirements."""
    console = Console()
    
    # Find biotope project root
    biotope_root = _find_biotope_root()
    if not biotope_root:
        click.echo("❌ Not in a biotope project. Run 'biotope init' first.")
        raise click.Abort
    
    # Load config
    config = load_biotope_config(biotope_root)
    validation_config = config.get("annotation_validation", {})
    
    console.print(f"\n[bold blue]Annotation Validation Configuration[/]")
    console.print(f"Enabled: {'✅' if validation_config.get('enabled', True) else '❌'}")
    
    # Show required fields
    required_fields = validation_config.get("minimum_required_fields", [])
    if required_fields:
        console.print(f"\n[bold green]Required Fields:[/]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Validation Rules", style="yellow")
        
        field_validation = validation_config.get("field_validation", {})
        for field in required_fields:
            rules = field_validation.get(field, {})
            field_type = rules.get("type", "any")
            
            validation_rules = []
            if "min_length" in rules:
                validation_rules.append(f"min_length: {rules['min_length']}")
            if "required_keys" in rules:
                validation_rules.append(f"required_keys: {', '.join(rules['required_keys'])}")
            
            table.add_row(field, field_type, "; ".join(validation_rules) if validation_rules else "none")
        
        console.print(table)
    else:
        console.print(f"\n[bold yellow]No required fields configured[/]")
        console.print("Use 'biotope config set-validation --field <field_name>' to add requirements")


@config.command()
@click.option(
    "--field",
    "-f",
    required=True,
    help="Field name to remove from required fields",
)
def remove_validation(field: str) -> None:
    """Remove a field from annotation validation requirements."""
    console = Console()
    
    # Find biotope project root
    biotope_root = _find_biotope_root()
    if not biotope_root:
        click.echo("❌ Not in a biotope project. Run 'biotope init' first.")
        raise click.Abort
    
    config_path = biotope_root / ".biotope" / "config" / "biotope.yaml"
    if not config_path.exists():
        click.echo("❌ Biotope configuration not found. Run 'biotope init' first.")
        raise click.Abort
    
    # Load current config
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        click.echo(f"❌ Error reading configuration: {e}")
        raise click.Abort
    
    # Remove field from required fields
    if "annotation_validation" in config:
        if field in config["annotation_validation"].get("minimum_required_fields", []):
            config["annotation_validation"]["minimum_required_fields"].remove(field)
            console.print(f"✅ Removed '{field}' from required fields")
        else:
            console.print(f"⚠️  Field '{field}' is not in required fields")
        
        # Remove field validation rules
        if "field_validation" in config["annotation_validation"]:
            if field in config["annotation_validation"]["field_validation"]:
                del config["annotation_validation"]["field_validation"][field]
                console.print(f"✅ Removed validation rules for '{field}'")
    
    # Save updated config
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        console.print("✅ Configuration updated successfully")
    except yaml.YAMLError as e:
        click.echo(f"❌ Error writing configuration: {e}")
        raise click.Abort


@config.command()
@click.option(
    "--enabled/--disabled",
    default=True,
    help="Enable or disable annotation validation",
)
def toggle_validation(enabled: bool) -> None:
    """Enable or disable annotation validation."""
    console = Console()
    
    # Find biotope project root
    biotope_root = _find_biotope_root()
    if not biotope_root:
        click.echo("❌ Not in a biotope project. Run 'biotope init' first.")
        raise click.Abort
    
    config_path = biotope_root / ".biotope" / "config" / "biotope.yaml"
    if not config_path.exists():
        click.echo("❌ Biotope configuration not found. Run 'biotope init' first.")
        raise click.Abort
    
    # Load current config
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        click.echo(f"❌ Error reading configuration: {e}")
        raise click.Abort
    
    # Initialize annotation_validation if it doesn't exist
    if "annotation_validation" not in config:
        config["annotation_validation"] = {}
    
    # Set enabled status
    config["annotation_validation"]["enabled"] = enabled
    
    # Save updated config
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        status = "enabled" if enabled else "disabled"
        console.print(f"✅ Annotation validation {status}")
    except yaml.YAMLError as e:
        click.echo(f"❌ Error writing configuration: {e}")
        raise click.Abort


def _find_biotope_root() -> Optional[Path]:
    """Find the biotope project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".biotope").exists():
            return current
        current = current.parent
    return None 