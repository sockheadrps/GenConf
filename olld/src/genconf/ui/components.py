from textual.widgets import Static, Input, Button, ListView, ListItem, Select, Label, Tabs, Tab, Footer
from textual.app import ComposeResult
from ..config.generator_list import generators

def add_input_fields(prefix: str) -> ComposeResult:
    """Add input fields with a prefix for Pre-Run or Post-Run sections."""
    fields = ["Fuel Level", "Battery VDC", "Run Hours", "Coolant Temp", "Leaks"]
    if prefix == "pre":
        fields.append("Oil Check")
    fields.append("Notes")
    
    for field in fields:
        label_id = f"{prefix}_{field.lower().replace(' ', '_')}_label"
        input_id = f"{prefix}_{field.lower().replace(' ', '_')}"
        yield Static(f"{field} ({prefix.capitalize()}):", id=label_id)
        yield Input(placeholder=f"Enter {field.lower()} ({prefix})", id=input_id)

def create_equipment_check_tab(current_month: str) -> ComposeResult:
    """Create the Equipment Check tab content."""
    with Static(id="equipment_check_content", classes="show"):
        yield Static(f"Current Month: {current_month.title()}", id="current_month_label")
        yield Static("Select Generator:", id="select_label")
        yield Select(
            options=[(gen, gen) for gen in generators],
            id="generator_select"
        )

        with Static(id="run_container"):
            with Static(id="pre_run_container"):
                yield Static("Pre-Run Check:", id="pre_run_label")
                yield from add_input_fields(prefix="pre")

            with Static(id="post_run_container"):
                yield Static("Post-Run Check:", id="post_run_label")
                yield from add_input_fields(prefix="post")

        yield Button("Save Entry", id="save_button", variant="success")
        yield Static("Recorded Entries:", id="entries_label")
        yield ListView(id="entries_view")
        yield Footer()

def create_database_tab(current_db: str, months: list) -> ComposeResult:
    """Create the Database tab content."""
    with Static(id="database_content"):
        yield Static(f"Database: {current_db}", id="db_instructions")
        
        with Static(id="db_controls"):
            yield Static("Select Month:")
            yield Select(
                options=[(month.title(), month) for month in months],
                id="month_select",
                prompt="Select month"
            )
            yield Static("Select Generator:")
            yield Select(
                options=[(gen, gen) for gen in generators],
                id="db_generator_select",
                prompt="Select generator"
            )
        
        with Static(id="db_button_container"):
            yield Button("Show Table Contents", id="show_all_button", variant="success")
            yield Button("Load for Editing", id="load_for_edit_button", variant="primary")
        
        with Static(id="db_entries_container"):
            with Static(id="pre_entries_container"):
                yield Static("Pre-Run Entries:", id="pre_entries_label")
                yield ListView(id="pre_database_entries_view")
            
            with Static(id="post_entries_container"):
                yield Static("Post-Run Entries:", id="post_entries_label") 
                yield ListView(id="post_database_entries_view")
        
        yield Footer()

def create_report_tab(months: list) -> ComposeResult:
    """Create the Report tab content."""
    with Static(id="report_content"):
        yield Static("Generate Monthly Reports", id="report_instructions")
        yield Static("Select Month:")
        yield Select(
            options=[(month.title(), month) for month in months],
            id="report_month_select",
            prompt="Select month"
        )
        yield Button("Generate CSV Reports", id="generate_report_button", variant="success")
        yield Footer()

def create_tabs() -> ComposeResult:
    """Create the main tab structure."""
    yield Tabs(
        Tab("Equipment Check", id="tab_equipment_check"),
        Tab("Database", id="tab_database"),
        Tab("Generate Report", id="tab_report")
    )

def create_list_item_from_entry(generator: str, month: str, pre_data: str, post_data: str) -> ListItem:
    """Create a ListItem widget for an entry."""
    entry_text = (
        f"Generator: {generator}\n"
        f"Month: {month.title()}\n"
        f"Pre-Run: {pre_data}\n"
        f"Post-Run: {post_data}\n"
    )
    return ListItem(Label(entry_text))