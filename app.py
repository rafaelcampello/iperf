from flask import Flask, render_template, request, redirect, url_for
import re
import plotly.graph_objects as go
from io import BytesIO
import base64
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
    if contains_timestamps:
        regex_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(\d+\.\d+)-(\d+\.\d+) sec.*\((\d+)%\)'
    else:
        regex_pattern = r'\[.*?\]\s+(\d+\.\d+)-(\d+\.\d+) sec.*\((\d+)%\)'
    
    for match in re.finditer(regex_pattern, iperf_results):
        if contains_timestamps:
            timestamp_str, time_start, time_end, loss_percentage = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            time = timestamp
        else:
            time_start, time_end, loss_percentage = match.groups()
            time = (float(time_start) + float(time_end)) / 2
        data.append((time, float(loss_percentage)))

    # Prepare data for graph
    times, loss_percentages = zip(*data) if data else ([], [])

    # Create a Plotly graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=loss_percentages, mode='markers+lines', hoverinfo='x+y'))
    fig.update_layout(
        xaxis_title='Time' + (' (Timestamp)' if contains_timestamps else ' (Seconds)'),
        yaxis_title='Packet Loss Percentage (%)',
        title='Packet Loss Over Time'
    )

    # Converts the Plotly graph into a base64 image
    img = BytesIO()
    fig.write_image(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.read()).decode()

    return render_template('results.html', graph_url=graph_url)

if __name__ == '__main__':
    app.run(debug=True)
