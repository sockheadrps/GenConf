import sqlite3
from pathlib import Path
from datetime import datetime
from ..config.generator_list import generators

class DatabaseManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.current_db = self.data_dir / "equipment_check.db"
        self.connection = None
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        self.available_tables = []
        self.init_db()

    def init_db(self):
        """Initialize SQLite database connection and tables."""
        self.connection = sqlite3.connect(self.current_db)
        cursor = self.connection.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        self.available_tables = [table[0] for table in cursor.fetchall()]
        
        if not self.available_tables:
            for month in self.months:
                for generator in generators:
                    gen_safe = generator.replace('-', '_').lower()
                    
                    # Create pre-run table
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {month}_{gen_safe}_pre (
                        fuel_level TEXT,
                        battery_vdc TEXT,
                        run_hours TEXT,
                        coolant_temp TEXT,
                        leaks TEXT,
                        oil_check TEXT,
                        notes TEXT,
                        last_updated DATE
                    )""")
                    
                    # Create post-run table
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {month}_{gen_safe}_post (
                        fuel_level TEXT,
                        battery_vdc TEXT,
                        run_hours TEXT,
                        coolant_temp TEXT,
                        leaks TEXT,
                        notes TEXT,
                        last_updated DATE
                    )""")
                    
                    # Insert initial empty row for each table
                    cursor.execute(f"""
                    INSERT INTO {month}_{gen_safe}_pre 
                    (fuel_level, battery_vdc, run_hours, coolant_temp, leaks, oil_check, notes, last_updated)
                    VALUES ('', '', '', '', '', '', '', CURRENT_DATE)
                    """)
                    
                    cursor.execute(f"""
                    INSERT INTO {month}_{gen_safe}_post
                    (fuel_level, battery_vdc, run_hours, coolant_temp, leaks, notes, last_updated)
                    VALUES ('', '', '', '', '', '', CURRENT_DATE)
                    """)
            
            self.connection.commit()
            
            # Update available tables list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            self.available_tables = [table[0] for table in cursor.fetchall()]

    def save_check_data(self, generator: str, pre_data: dict, post_data: dict):
        """Save pre and post run check data to database."""
        cursor = self.connection.cursor()
        gen_safe = generator.replace('-', '_').lower()
        current_month = datetime.now().strftime("%B").lower()
        
        # Update pre-run data
        pre_values = (
            pre_data.get('fuel_level', ''),
            pre_data.get('battery_vdc', ''),
            pre_data.get('run_hours', ''),
            pre_data.get('coolant_temp', ''),
            pre_data.get('leaks', ''),
            pre_data.get('oil_check', ''),
            pre_data.get('notes', '')
        )
        
        cursor.execute(f"""
        UPDATE {current_month}_{gen_safe}_pre 
        SET fuel_level=?, battery_vdc=?, run_hours=?, coolant_temp=?, leaks=?, 
            oil_check=?, notes=?, last_updated=CURRENT_DATE
        """, pre_values)
        
        # Update post-run data
        post_values = (
            post_data.get('fuel_level', ''),
            post_data.get('battery_vdc', ''),
            post_data.get('run_hours', ''),
            post_data.get('coolant_temp', ''),
            post_data.get('leaks', ''),
            post_data.get('notes', '')
        )
        
        cursor.execute(f"""
        UPDATE {current_month}_{gen_safe}_post 
        SET fuel_level=?, battery_vdc=?, run_hours=?, coolant_temp=?, leaks=?, 
            notes=?, last_updated=CURRENT_DATE
        """, post_values)
        
        self.connection.commit()

    def get_entries(self, month: str, generator: str):
        """Retrieve entries for a specific month and generator."""
        cursor = self.connection.cursor()
        gen_safe = generator.replace('-', '_').lower()
        
        # Get pre-run entries
        pre_table = f"{month}_{gen_safe}_pre"
        cursor.execute(f"SELECT * FROM {pre_table}")
        pre_entries = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({pre_table})")
        pre_columns = [col[1] for col in cursor.fetchall()]
        
        # Get post-run entries
        post_table = f"{month}_{gen_safe}_post"
        cursor.execute(f"SELECT * FROM {post_table}")
        post_entries = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({post_table})")
        post_columns = [col[1] for col in cursor.fetchall()]
        
        return {
            'pre': {'columns': pre_columns, 'entries': pre_entries},
            'post': {'columns': post_columns, 'entries': post_entries}
        }

    def __del__(self):
        """Ensure database connection is closed."""
        if self.connection:
            self.connection.close()