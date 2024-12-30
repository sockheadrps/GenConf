import csv
from pathlib import Path
from datetime import datetime

def generate_monthly_reports(month: str, generators: list, db_connection):
    """Generate CSV reports for the specified month."""
    data_dir = Path("data/reports")
    data_dir.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate pre-run report
    _generate_pre_run_report(month, generators, db_connection, data_dir, timestamp)
    
    # Generate post-run report
    _generate_post_run_report(month, generators, db_connection, data_dir, timestamp)

def _generate_pre_run_report(month: str, generators: list, db_connection, data_dir: Path, timestamp: str):
    """Generate pre-run CSV report."""
    report_path = data_dir / f"{month}_pre_run_report_{timestamp}.csv"
    
    with open(report_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Generator', 'Fuel Level', 'Battery VDC', 'Run Hours', 
                        'Coolant Temp', 'Leaks', 'Oil Check', 'Notes', 'Last Updated'])
        
        cursor = db_connection.cursor()
        for generator in generators:
            gen_safe = generator.replace('-', '_').lower()
            cursor.execute(f"""
                SELECT * FROM {month}_{gen_safe}_pre
                WHERE last_updated = (
                    SELECT MAX(last_updated) 
                    FROM {month}_{gen_safe}_pre
                )
            """)
            row = cursor.fetchone()
            if row:
                writer.writerow([generator] + list(row))

def _generate_post_run_report(month: str, generators: list, db_connection, data_dir: Path, timestamp: str):
    """Generate post-run CSV report."""
    report_path = data_dir / f"{month}_post_run_report_{timestamp}.csv"
    
    with open(report_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Generator', 'Fuel Level', 'Battery VDC', 'Run Hours', 
                        'Coolant Temp', 'Leaks', 'Notes', 'Last Updated'])
        
        cursor = db_connection.cursor()
        for generator in generators:
            gen_safe = generator.replace('-', '_').lower()
            cursor.execute(f"""
                SELECT * FROM {month}_{gen_safe}_post
                WHERE last_updated = (
                    SELECT MAX(last_updated) 
                    FROM {month}_{gen_safe}_post
                )
            """)
            row = cursor.fetchone()
            if row:
                writer.writerow([generator] + list(row))