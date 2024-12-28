from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Button, ListView, ListItem, Select, Label, Tabs, Tab
from genconf.database.db_manager import DatabaseManager
from genconf.ui.components import (
    create_tabs, 
    create_equipment_check_tab, 
    create_database_tab, 
    create_report_tab,
    create_list_item_from_entry,
    add_input_fields
)
from genconf.ui.styles import APP_CSS
from genconf.utils.report_generator import generate_monthly_reports
from datetime import datetime
from genconf.config.generator_list import generators

class EquipmentCheckApp(App):
    """A Textual App for recording Pre-Run and Post-Run equipment check details."""
    
    CSS = APP_CSS

    def __init__(self):
        super().__init__()
        self.entries = []
        self.db = DatabaseManager()
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        self.generators = generators
        self.current_month = datetime.now().strftime("%B").lower()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield from create_tabs()
        yield from create_equipment_check_tab(self.current_month)
        yield from create_database_tab(self.db.current_db, self.months)
        yield from create_report_tab(self.months)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab switching."""
        if event.tab.id == "tab_equipment_check":
            self.query_one("#equipment_check_content").add_class("show")
            self.query_one("#database_content").remove_class("show")
            self.query_one("#report_content").remove_class("show")
        elif event.tab.id == "tab_database":
            self.query_one("#database_content").add_class("show")
            self.query_one("#equipment_check_content").remove_class("show")
            self.query_one("#report_content").remove_class("show")
        elif event.tab.id == "tab_report":
            self.query_one("#report_content").add_class("show")
            self.query_one("#equipment_check_content").remove_class("show")
            self.query_one("#database_content").remove_class("show")

    def collect_data(self, prefix: str) -> dict:
        """Collect data from input fields."""
        fields = [
            "fuel_level", "battery_vdc", "run_hours",
            "coolant_temp", "leaks"
        ]
        if prefix == "pre":
            fields.append("oil_check")
        fields.append("notes")
        
        data = {}
        for field in fields:
            widget_id = f"#{prefix}_{field}"
            input_widget = self.query_one(widget_id, Input)
            if field != "notes" and not input_widget.value.strip():
                return {}
            data[field] = input_widget.value.strip()
        return data

    def clear_data(self, prefix: str) -> None:
        """Clear input fields."""
        fields = [
            "fuel_level", "battery_vdc", "run_hours",
            "coolant_temp", "leaks", "oil_check", "notes"
        ]
        for field in fields:
            try:
                widget = self.query_one(f"#{prefix}_{field}", Input)
                widget.value = ""
            except:
                continue

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save_button":
            self._handle_save_button()
        elif event.button.id == "show_all_button":
            self._handle_show_all_button()
        elif event.button.id == "load_for_edit_button":
            self._handle_load_for_edit_button()
        elif event.button.id == "generate_report_button":
            self._handle_generate_report_button()

    def _handle_save_button(self):
        """Handle save button press."""
        selected_generator = self.query_one("#generator_select", Select).value
        
        # Check if a generator is selected
        if not selected_generator:
            # You might want to show an error message to the user here
            return
            
        pre_data = self.collect_data("pre")
        post_data = self.collect_data("post")

        if selected_generator and pre_data and post_data:
            self.db.save_check_data(selected_generator, pre_data, post_data)
            
            list_item = create_list_item_from_entry(
                selected_generator,
                self.current_month,
                str(pre_data),
                str(post_data)
            )
            self.entries.append(list_item)
            self.query_one("#entries_view", ListView).append(list_item)

            for prefix in ["pre", "post"]:
                self.clear_data(prefix)
        else:
            # You might want to show an error message to the user here
            pass

    def _handle_show_all_button(self):
        """Handle show all button press."""
        month = self.query_one("#month_select", Select).value
        generator = self.query_one("#db_generator_select", Select).value
        
        if month and generator:
            entries = self.db.get_entries(month, generator)
            
            pre_list_view = self.query_one("#pre_database_entries_view", ListView)
            post_list_view = self.query_one("#post_database_entries_view", ListView)
            
            pre_list_view.clear()
            post_list_view.clear()
            
            for entry in entries['pre']['entries']:
                entry_text = "\n".join(f"{col}: {val}" for col, val in zip(entries['pre']['columns'], entry))
                pre_list_view.append(ListItem(Label(entry_text)))
            
            for entry in entries['post']['entries']:
                entry_text = "\n".join(f"{col}: {val}" for col, val in zip(entries['post']['columns'], entry))
                post_list_view.append(ListItem(Label(entry_text)))

    def _handle_load_for_edit_button(self):
        """Handle load for edit button press."""
        month = self.query_one("#month_select", Select).value
        generator = self.query_one("#db_generator_select", Select).value
        
        if month and generator:
            entries = self.db.get_entries(month, generator)
            
            # Switch to equipment check tab
            tabs = self.query_one(Tabs)
            tabs.active = "tab_equipment_check"
            
            # Set generator select
            self.query_one("#generator_select", Select).value = generator
            
            # Fill pre-run fields
            if entries['pre']['entries']:
                for field, value in zip(entries['pre']['columns'], entries['pre']['entries'][0]):
                    if field != 'last_updated':
                        try:
                            widget = self.query_one(f"#pre_{field}", Input)
                            widget.value = value or ""
                        except:
                            continue
            
            # Fill post-run fields
            if entries['post']['entries']:
                for field, value in zip(entries['post']['columns'], entries['post']['entries'][0]):
                    if field != 'last_updated':
                        try:
                            widget = self.query_one(f"#post_{field}", Input)
                            widget.value = value or ""
                        except:
                            continue

    def _handle_generate_report_button(self):
        """Handle generate report button press."""
        month = self.query_one("#report_month_select", Select).value
        if month:
            generate_monthly_reports(month, self.generators, self.db.connection)