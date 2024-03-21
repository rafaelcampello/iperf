from flask import Flask, render_template, request, redirect, url_for
import re
import plotly.graph_objects as go
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_results():
    file = request.files.get('iperf_results_file')
    if not file or file.filename == '':
        return redirect(url_for('index'))
    
    iperf_results = file.read().decode('utf-8')

    # Verificar se contém timestamps
    contains_timestamps = bool(re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', iperf_results))
    
    data = []
    regex_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(\d+\.\d+)-(\d+\.\d+) sec.*?(\d+)/(\d+)\s+\((\d+\.\d+)%\)' if contains_timestamps else r'\[.*?\]\s+(\d+\.\d+)-(\d+\.\d+) sec.*?(\d+)/(\d+)\s+\((\d+\.\d+)%\)'
    
    total_loss = "N/A"
    for match in re.finditer(regex_pattern, iperf_results):
        if contains_timestamps:
            timestamp_str, time_start, time_end, _, _, loss_percentage = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            time = timestamp
        else:
            time_start, time_end, _, _, loss_percentage = match.groups()
            time = (float(time_start) + float(time_end)) / 2
        data.append((time, float(loss_percentage)))

    # Extract the total packet loss percentage from the last matching group
    if data:
        total_loss = match.group(6) + "%"  # Assuming the last match has the total loss

    times, loss_percentages = zip(*data) if data else ([], [])

    # Skipping the Plotly figure creation and base64 conversion for brevity

    return render_template('results.html', graph_url="PLOTLY_GRAPH_URL", total_loss=total_loss
    # Create a Plotly graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=loss_percentages, mode='lines+markers', name='Loss %'))
    fig.update_layout(
        title='iPerf Test Results: Packet Loss Over Time',
        xaxis=dict(
            title='Time' + (' (Timestamps)' if contains_timestamps else ' (Seconds)'),
            type='date' if contains_timestamps else 'linear'
        ),
        yaxis=dict(
            title='Packet Loss (%)',
        ),
        hovermode='closest'
    )

    # Serialize the figure to JSON for embedding in the HTML
    graph_json = fig.to_json()

    return render_template('results.html', graph_json=graph_json, total_loss=total_loss)
