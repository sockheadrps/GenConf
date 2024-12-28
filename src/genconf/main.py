from app.equipment_check_app import EquipmentCheckApp

if __name__ == "__main__":
    EquipmentCheckApp().run()




# from textual.app import App, ComposeResult
# from textual.widgets import Header, Footer, Static, Input, Button, ListView, ListItem, Select, Label, Tabs, Tab
# import sqlite3
# import os
# from pathlib import Path
# from datetime import datetime
# import csv

# class EquipmentCheckApp(App):
#     """A Textual App for recording Pre-Run and Post-Run equipment check details."""

#     CSS = """
#     #title {
#         padding: 1;
#     }
    
#     #instructions {
#         padding: 1;
#     }
    
#     #select_label, #pre_run_label, #post_run_label, #entries_label {
#         padding: 1;
#     }
    
#     Input {
#         margin: 1;
#         width: 100%;
#     }
    
#     Select {
#         margin: 1;
#         width: 100%;
#     }
    
#     Button {
#         margin: 1;
#         width: 100%;
#     }
    
#     ListView {
#         height: 10;
#         border: solid green;
#         margin: 1;
#     }

#     #run_container {
#         layout: horizontal;
#         height: auto;
#     }

#     #pre_run_container, #post_run_container {
#         width: 50%;
#         height: auto;
#         padding: 1;
#     }

#     #db_controls {
#         layout: vertical;
#         height: auto;
#         margin: 1;
#     }

#     #equipment_check_content {
#         display: none;
#     }

#     #database_content {
#         display: none;
#     }

#     #report_content {
#         display: none;
#     }

#     #equipment_check_content.show {
#         display: block;
#     }

#     #database_content.show {
#         display: block;
#     }

#     #report_content.show {
#         display: block;
#     }

#     #db_entries_container {
#         layout: horizontal;
#         height: auto;
#     }

#     #pre_entries_container, #post_entries_container {
#         width: 50%;
#         height: auto;
#         padding: 1;
#     }

#     #db_button_container {
#         layout: horizontal;
#         height: auto;
#         margin: 1;
#     }

#     #db_button_container Button {
#         width: 50%;
#     }
#     """

#     def __init__(self):
#         super().__init__()
#         self.entries = []
#         # Create data directory if it doesn't exist
#         data_dir = Path("data")
#         data_dir.mkdir(exist_ok=True)
#         self.current_db = data_dir / "equipment_check.db"
#         self.db_connection = None
#         self.init_db()
#         self.months = ['january', 'february', 'march', 'april', 'may', 'june',
#                       'july', 'august', 'september', 'october', 'november', 'december']
#         self.generators = [
#             "GEN-A3", "GEN-A2", "GEN-B3", "GEN-B2", "GEN-C3", "GEN-C2",
#             "GEN-D3", "GEN-D2", "GEN-R3", "GEN-R2", "GEN-A1", "GEN-B1",
#             "GEN-C1", "GEN-D1", "GEN-E2", "GEN-R1", "GEN-H3", "GEN-I3",
#             "GEN-J3", "GEN-G3", "GEN-F3", "GEN-E3"
#         ]
#         self.current_month = datetime.now().strftime("%B").lower()

#     def init_db(self):
#         """Initialize SQLite database connection and get available tables."""
#         self.db_connection = sqlite3.connect(self.current_db)
#         cursor = self.db_connection.cursor()
        
#         # Get list of tables
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#         self.available_tables = [table[0] for table in cursor.fetchall()]
        
#         if not self.available_tables:
#             # Create tables for each month and generator
#             months = ['january', 'february', 'march', 'april', 'may', 'june',
#                      'july', 'august', 'september', 'october', 'november', 'december']
            
#             generators = [
#                 "GEN-A3", "GEN-A2", "GEN-B3", "GEN-B2", "GEN-C3", "GEN-C2",
#                 "GEN-D3", "GEN-D2", "GEN-R3", "GEN-R2", "GEN-A1", "GEN-B1",
#                 "GEN-C1", "GEN-D1", "GEN-E2", "GEN-R1", "GEN-H3", "GEN-I3",
#                 "GEN-J3", "GEN-G3", "GEN-F3", "GEN-E3"
#             ]
            
#             for month in months:
#                 for generator in generators:
#                     gen_safe = generator.replace('-', '_').lower()
                    
#                     # Create pre-run table
#                     cursor.execute(f"""
#                     CREATE TABLE IF NOT EXISTS {month}_{gen_safe}_pre (
#                         fuel_level TEXT,
#                         battery_vdc TEXT,
#                         run_hours TEXT,
#                         coolant_temp TEXT,
#                         leaks TEXT,
#                         oil_check TEXT,
#                         notes TEXT,
#                         last_updated DATE
#                     )""")
                    
#                     # Create post-run table
#                     cursor.execute(f"""
#                     CREATE TABLE IF NOT EXISTS {month}_{gen_safe}_post (
#                         fuel_level TEXT,
#                         battery_vdc TEXT,
#                         run_hours TEXT,
#                         coolant_temp TEXT,
#                         leaks TEXT,
#                         notes TEXT,
#                         last_updated DATE
#                     )""")
                    
#                     # Insert initial empty row for each table
#                     cursor.execute(f"""
#                     INSERT INTO {month}_{gen_safe}_pre 
#                     (fuel_level, battery_vdc, run_hours, coolant_temp, leaks, oil_check, notes, last_updated)
#                     VALUES ('', '', '', '', '', '', '', CURRENT_DATE)
#                     """)
                    
#                     cursor.execute(f"""
#                     INSERT INTO {month}_{gen_safe}_post
#                     (fuel_level, battery_vdc, run_hours, coolant_temp, leaks, notes, last_updated)
#                     VALUES ('', '', '', '', '', '', CURRENT_DATE)
#                     """)
                
#             self.db_connection.commit()
            
#             # Update available tables list
#             cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#             self.available_tables = [table[0] for table in cursor.fetchall()]

#     def compose(self) -> ComposeResult:
#         """Create child widgets for the app."""
#         yield Tabs(
#             Tab("Equipment Check", id="tab_equipment_check"),
#             Tab("Database", id="tab_database"),
#             Tab("Generate Report", id="tab_report")
#         )
        
#         # Equipment Check Tab content
#         with Static(id="equipment_check_content", classes="show"):
#             yield Static(f"Current Month: {self.current_month.title()}", id="current_month_label")
#             yield Static("Select Generator:", id="select_label")
#             yield Select(
#                 options=[(gen, gen) for gen in self.generators],
#                 id="generator_select"
#             )

#             # Container for Pre-Run and Post-Run sections
#             with Static(id="run_container"):
#                 # Pre-Run Section
#                 with Static(id="pre_run_container"):
#                     yield Static("Pre-Run Check:", id="pre_run_label")
#                     yield from self.add_input_fields(prefix="pre")

#                 # Post-Run Section  
#                 with Static(id="post_run_container"):
#                     yield Static("Post-Run Check:", id="post_run_label")
#                     yield from self.add_input_fields(prefix="post")

#             # Save button
#             yield Button("Save Entry", id="save_button", variant="success")

#             # ListView for recorded entries
#             yield Static("Recorded Entries:", id="entries_label")
#             yield ListView(id="entries_view")

#             yield Footer()

#         # Database Tab content
#         with Static(id="database_content"):
#             yield Static(f"Database: {self.current_db}", id="db_instructions")
            
#             # Database controls container
#             with Static(id="db_controls"):
#                 yield Static("Select Month:")
#                 yield Select(
#                     options=[(month.title(), month) for month in self.months],
#                     id="month_select",
#                     prompt="Select month"
#                 )
#                 yield Static("Select Generator:")
#                 yield Select(
#                     options=[(gen, gen) for gen in self.generators],
#                     id="db_generator_select",
#                     prompt="Select generator"
#                 )
            
#             # Container for database action buttons
#             with Static(id="db_button_container"):
#                 yield Button("Show Table Contents", id="show_all_button", variant="success")
#                 yield Button("Load for Editing", id="load_for_edit_button", variant="primary")
            
#             # Container for Pre-Run and Post-Run database entries
#             with Static(id="db_entries_container"):
#                 with Static(id="pre_entries_container"):
#                     yield Static("Pre-Run Entries:", id="pre_entries_label")
#                     yield ListView(id="pre_database_entries_view")
                
#                 with Static(id="post_entries_container"):
#                     yield Static("Post-Run Entries:", id="post_entries_label") 
#                     yield ListView(id="post_database_entries_view")
            
#             yield Footer()

#         # Report Tab content
#         with Static(id="report_content"):
#             yield Static("Generate Monthly Reports", id="report_instructions")
#             yield Static("Select Month:")
#             yield Select(
#                 options=[(month.title(), month) for month in self.months],
#                 id="report_month_select",
#                 prompt="Select month"
#             )
#             yield Button("Generate CSV Reports", id="generate_report_button", variant="success")
#             yield Footer()

#     def add_input_fields(self, prefix: str):
#         """Add input fields with a prefix for Pre-Run or Post-Run sections."""
#         fields = ["Fuel Level", "Battery VDC", "Run Hours", "Coolant Temp", "Leaks"]
#         if prefix == "pre":
#             fields.append("Oil Check")
#         fields.append("Notes")
        
#         for field in fields:
#             label_id = f"{prefix}_{field.lower().replace(' ', '_')}_label"
#             input_id = f"{prefix}_{field.lower().replace(' ', '_')}"
#             yield Static(f"{field} ({prefix.capitalize()}):", id=label_id)
#             yield Input(placeholder=f"Enter {field.lower()} ({prefix})", id=input_id)

#     def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
#         """Handle tab switching."""
#         if event.tab.id == "tab_equipment_check":
#             self.query_one("#equipment_check_content").add_class("show")
#             self.query_one("#database_content").remove_class("show")
#             self.query_one("#report_content").remove_class("show")
#         elif event.tab.id == "tab_database":
#             self.query_one("#database_content").add_class("show")
#             self.query_one("#equipment_check_content").remove_class("show")
#             self.query_one("#report_content").remove_class("show")
#         elif event.tab.id == "tab_report":
#             self.query_one("#report_content").add_class("show")
#             self.query_one("#equipment_check_content").remove_class("show")
#             self.query_one("#database_content").remove_class("show")

#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         """Handle button presses."""
#         if event.button.id == "save_button":
#             # Retrieve generator selection
#             selected_generator = self.query_one("#generator_select", Select).value

#             # Collect Pre-Run and Post-Run data
#             pre_data = self.collect_data("pre")
#             post_data = self.collect_data("post")

#             if selected_generator and pre_data and post_data:
#                 # Update entry in database using current month
#                 self.save_to_db(selected_generator, pre_data, post_data)
                
#                 # Create entry text
#                 entry_text = (
#                     f"Generator: {selected_generator}\n"
#                     f"Month: {self.current_month.title()}\n"
#                     f"Pre-Run: {pre_data}\n"
#                     f"Post-Run: {post_data}\n"
#                 )
                
#                 # Create ListItem widget with the entry text
#                 list_item = ListItem(Label(entry_text))
#                 # Store entry and update ListView
#                 self.entries.append(entry_text)
#                 self.query_one("#entries_view", ListView).append(list_item)

#                 # Clear all inputs
#                 for prefix in ["pre", "post"]:
#                     self.clear_data(prefix)
#             else:
#                 self.query_one("#instructions", Static).update(
#                     "Please fill all required fields for both Pre-Run and Post-Run before saving."
#                 )
#         elif event.button.id == "show_all_button":
#             self.show_database_entries()
#         elif event.button.id == "load_for_edit_button":
#             self.load_for_editing()
#         elif event.button.id == "generate_report_button":
#             self.generate_reports()

#     def generate_reports(self) -> None:
#         """Generate CSV reports for the selected month."""
#         month = self.query_one("#report_month_select", Select).value
#         if not month:
#             return

#         cursor = self.db_connection.cursor()

#         # Generate pre-run report
#         with open(f'data/{month}_pre_run_report.csv', 'w', newline='') as f:
#             writer = csv.writer(f)
#             # Write headers
#             writer.writerow(['Generator', 'Fuel Level', 'Battery VDC', 'Run Hours', 
#                            'Coolant Temp', 'Leaks', 'Oil Check', 'Notes', 'Last Updated'])
            
#             # Get data for each generator
#             for generator in self.generators:
#                 gen_safe = generator.replace('-', '_').lower()
#                 cursor.execute(f"SELECT * FROM {month}_{gen_safe}_pre")
#                 row = cursor.fetchone()
#                 if row:
#                     writer.writerow([generator] + list(row))

#         # Generate post-run report
#         with open(f'data/{month}_post_run_report.csv', 'w', newline='') as f:
#             writer = csv.writer(f)
#             # Write headers
#             writer.writerow(['Generator', 'Fuel Level', 'Battery VDC', 'Run Hours', 
#                            'Coolant Temp', 'Leaks', 'Notes', 'Last Updated'])
            
#             # Get data for each generator
#             for generator in self.generators:
#                 gen_safe = generator.replace('-', '_').lower()
#                 cursor.execute(f"SELECT * FROM {month}_{gen_safe}_post")
#                 row = cursor.fetchone()
#                 if row:
#                     writer.writerow([generator] + list(row))

#     def collect_data(self, prefix: str) -> str:
#         """Collect data for a given section (Pre-Run or Post-Run)."""
#         fields = [
#             "fuel_level", "battery_vdc", "run_hours",
#             "coolant_temp", "leaks"
#         ]
#         if prefix == "pre":
#             fields.append("oil_check")
#         fields.append("notes")
        
#         try:
#             data = {}
#             for field in fields:
#                 widget_id = f"#{prefix}_{field}"
#                 input_widget = self.query_one(widget_id, Input)
#                 if field != "notes" and not input_widget.value.strip():
#                     return ""
#                 data[field.replace('_', ' ').capitalize()] = input_widget.value.strip()

#             return ', '.join([f"{key}: {value}" for key, value in data.items() if value])
#         except Exception as e:
#             return f"Error: {e}"

#     def clear_data(self, prefix: str) -> None:
#         """Clear data fields for a given section (Pre-Run or Post-Run)."""
#         fields = [
#             "fuel_level", "battery_vdc", "run_hours",
#             "coolant_temp", "leaks", "oil_check", "notes"
#         ]
#         for field in fields:
#             widget_id = f"#{prefix}_{field}"
#             try:
#                 input_widget = self.query_one(widget_id, Input)
#                 input_widget.value = ""
#             except:
#                 continue

#     def save_to_db(self, generator, pre_data, post_data):
#         """Save the check data to SQLite database."""
#         cursor = self.db_connection.cursor()
#         gen_safe = generator.replace('-', '_').lower()
        
#         # Parse the data into individual fields
#         pre_dict = dict(item.split(": ") for item in pre_data.split(", "))
#         post_dict = dict(item.split(": ") for item in post_data.split(", "))
        
#         # Update pre-run data
#         pre_values = (
#             pre_dict.get('Fuel level', ''),
#             pre_dict.get('Battery vdc', ''),
#             pre_dict.get('Run hours', ''),
#             pre_dict.get('Coolant temp', ''),
#             pre_dict.get('Leaks', ''),
#             pre_dict.get('Oil check', ''),
#             pre_dict.get('Notes', ''),
#             'CURRENT_DATE'
#         )
        
#         cursor.execute(f"""
#         UPDATE {self.current_month}_{gen_safe}_pre 
#         SET fuel_level=?, battery_vdc=?, run_hours=?, coolant_temp=?, leaks=?, 
#             oil_check=?, notes=?, last_updated=CURRENT_DATE
#         """, pre_values[:-1])
        
#         # Update post-run data
#         post_values = (
#             post_dict.get('Fuel level', ''),
#             post_dict.get('Battery vdc', ''),
#             post_dict.get('Run hours', ''),
#             post_dict.get('Coolant temp', ''),
#             post_dict.get('Leaks', ''),
#             post_dict.get('Notes', ''),
#             'CURRENT_DATE'
#         )
        
#         cursor.execute(f"""
#         UPDATE {self.current_month}_{gen_safe}_post 
#         SET fuel_level=?, battery_vdc=?, run_hours=?, coolant_temp=?, leaks=?, 
#             notes=?, last_updated=CURRENT_DATE
#         """, post_values[:-1])
        
#         self.db_connection.commit()

#     def show_database_entries(self) -> None:
#         """Show all entries from selected table in the database tab."""
#         month = self.query_one("#month_select", Select).value
#         generator = self.query_one("#db_generator_select", Select).value
        
#         if not all([month, generator]):
#             return
            
#         gen_safe = generator.replace('-', '_').lower()
        
#         cursor = self.db_connection.cursor()
        
#         # Clear both list views
#         self.query_one("#pre_database_entries_view", ListView).clear()
#         self.query_one("#post_database_entries_view", ListView).clear()
        
#         # Get and display pre-run entries
#         pre_table = f"{month}_{gen_safe}_pre"
#         cursor.execute(f"SELECT * FROM {pre_table}")
#         pre_entries = cursor.fetchall()
        
#         cursor.execute(f"PRAGMA table_info({pre_table})")
#         pre_columns = [col[1] for col in cursor.fetchall()]
        
#         pre_list_view = self.query_one("#pre_database_entries_view", ListView)
#         for entry in pre_entries:
#             entry_text = "\n".join(f"{col}: {val}" for col, val in zip(pre_columns, entry))
#             pre_list_view.append(ListItem(Label(entry_text)))
            
#         # Get and display post-run entries
#         post_table = f"{month}_{gen_safe}_post"
#         cursor.execute(f"SELECT * FROM {post_table}")
#         post_entries = cursor.fetchall()
        
#         cursor.execute(f"PRAGMA table_info({post_table})")
#         post_columns = [col[1] for col in cursor.fetchall()]
        
#         post_list_view = self.query_one("#post_database_entries_view", ListView)
#         for entry in post_entries:
#             entry_text = "\n".join(f"{col}: {val}" for col, val in zip(post_columns, entry))
#             post_list_view.append(ListItem(Label(entry_text)))

#     def load_for_editing(self) -> None:
#         """Load selected data into equipment check tab for editing."""
#         month = self.query_one("#month_select", Select).value
#         generator = self.query_one("#db_generator_select", Select).value
        
#         if not all([month, generator]):
#             return
            
#         # Switch to equipment check tab
#         tabs = self.query_one(Tabs)
#         tabs.active = "tab_equipment_check"
        
#         # Set generator select
#         self.query_one("#generator_select", Select).value = generator
        
#         # Get latest entries from database
#         cursor = self.db_connection.cursor()
#         gen_safe = generator.replace('-', '_').lower()
        
#         # Get pre-run data
#         cursor.execute(f"""
#         SELECT fuel_level, battery_vdc, run_hours, coolant_temp, leaks, oil_check, notes 
#         FROM {month}_{gen_safe}_pre
#         """)
#         pre_data = cursor.fetchone()
        
#         if pre_data:
#             fields = ["fuel_level", "battery_vdc", "run_hours", "coolant_temp", "leaks", "oil_check", "notes"]
#             for field, value in zip(fields, pre_data):
#                 try:
#                     widget = self.query_one(f"#pre_{field}", Input)
#                     widget.value = value or ""
#                 except:
#                     continue
        
#         # Get post-run data
#         cursor.execute(f"""
#         SELECT fuel_level, battery_vdc, run_hours, coolant_temp, leaks, notes 
#         FROM {month}_{gen_safe}_post
#         """)
#         post_data = cursor.fetchone()
        
#         if post_data:
#             fields = ["fuel_level", "battery_vdc", "run_hours", "coolant_temp", "leaks", "notes"]
#             for field, value in zip(fields, post_data):
#                 try:
#                     widget = self.query_one(f"#post_{field}", Input)
#                     widget.value = value or ""
#                 except:
#                     continue

# if __name__ == "__main__":
#     EquipmentCheckApp().run()
