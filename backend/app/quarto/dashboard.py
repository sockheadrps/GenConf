

import plotly.graph_objects as go
from backend.app.db.db_manager import DatabaseManager


def fetch_gen_data():
    db_manager = DatabaseManager()
    
    data = db_manager.all_gen_data('december', completed_only=True)
    return data


def time_to_decimal(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours + minutes / 60

def preprocess_data(data):
    processed_data = {}
    data_dict = {
        'fuel_level': data[0],
        'battery_vdc': data[1], 
        'run_hours': data[2],
        'coolant_temp': data[3],
        'leaks': data[4],
        'notes': data[5],
        'last_updated': data[6]
    }
    
    for key, value in data_dict.items():
        if key == 'run_hours' and isinstance(value, str):
            processed_data[key] = time_to_decimal(value)  # Convert "HH:MM" to decimal hours
        elif key == 'coolant_temp' and isinstance(value, str):
            processed_data[key] = float(value)  # Convert string to float
        else:
            processed_data[key] = value
    return processed_data

data = fetch_gen_data()
# Process data for all generators
gen_temps = {}
for gen in data:
    processed = preprocess_data(data[gen]['post'])
    if 'coolant_temp' in processed:
        gen_temps[gen] = processed['run_hours']

# Sort generators by run hours
sorted_gens = dict(sorted(gen_temps.items(), key=lambda x: x[1]))

# Prepare data for plotting
gens = list(sorted_gens.keys())
hours = list(sorted_gens.values())

# Create interactive bar plot with Plotly
fig = go.Figure(data=[
    go.Bar(
        x=gens,
        y=hours,
        text=[f'{h:.1f} hrs' for h in hours],
        textposition='auto',
        hovertemplate='Generator: %{x}<br>Run Hours: %{y:.1f}<extra></extra>',
        marker_color='rgb(55, 83, 109)'
    )
])

# Update layout with better styling
fig.update_layout(
    title={
        'text': 'Post-Run Run Hours Across All Generators',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}
    },
    xaxis_title='Generator',
    yaxis_title='Run Hours',
    xaxis_tickangle=-45,
    plot_bgcolor='white',
    showlegend=False,
    height=600,
    margin=dict(t=100, l=70, r=40, b=80),
    hoverlabel=dict(bgcolor="white", font_size=14),
)

# Add grid lines
fig.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='lightgray'
)

# Show the interactive plot
fig.show()