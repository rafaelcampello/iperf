from flask import Flask, render_template, request, redirect, url_for
import re
import plotly.graph_objects as go
from datetime import datetime
import webbrowser
from threading import Timer
import sys
import os

app = Flask(__name__)

# Adjust the template and static folder paths for PyInstaller
if getattr(sys, 'frozen', False):  # Check if running as a compiled app
    app.template_folder = os.path.join(sys._MEIPASS, 'templates')
    app.static_folder = os.path.join(sys._MEIPASS, 'static')

# Function to open the browser automatically after the server starts
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

# Route to render the main form page        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_results():
    file = request.files.get('iperf_results_file')
    if not file or file.filename == '':
        return redirect(url_for('index'))
    
    iperf_results = file.read().decode('utf-8')

    contains_timestamps = bool(re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', iperf_results))
    data = []
    total_loss = "N/A"
    
    if contains_timestamps:
        regex_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(\d+\.\d+)-(\d+\.\d+) sec.*\((\d+)%\)'
    else:
        regex_pattern = r'\[.*?\]\s+(\d+\.\d+)-(\d+\.\d+) sec.*\((\d+)%\)'
    
    for match in re.finditer(regex_pattern, iperf_results):
        if contains_timestamps:
            timestamp_str, _, _, loss_percentage = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            time = timestamp
        else:
            time_start, time_end, loss_percentage = match.groups()
            time = (float(time_start) + float(time_end)) / 2
        data.append((time, float(loss_percentage)))
    
    if data:
        times, loss_percentages = zip(*data)

        # Find total packets sent and received from the last line of results
        last_line = iperf_results.splitlines()[-1]
        total_sent_match = re.search(r'(\d+)/(\d+)', last_line)
        if total_sent_match:
            total_received = int(total_sent_match.group(1))
            total_sent = int(total_sent_match.group(2))
            if total_sent > 0:
                total_loss_percentage = (1 - (total_received / total_sent)) * 100
                total_loss = f"{total_loss_percentage:.10f}%"
            else:
                total_loss = "0.0000000000%"
        
        # Create a Plotly graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=loss_percentages, mode='markers+lines', name='Loss %'))
        fig.update_layout(
            title='iPerf Test Results: Packet Loss Over Time',
            xaxis=dict(
                title='Time' + (' (Timestamps)' if contains_timestamps else ' (Seconds)'),
                type='date' if contains_timestamps else 'linear'
            ),
            yaxis=dict(
                title='Packet Loss Percentage (%)',
            ),
            hovermode='closest',
            width=1200,  # Adjust this value to make the graph wider
            height=600   # You can adjust the height as well if needed
        )

        graph_json = fig.to_json()
    else:
        graph_json = None

    return render_template('results.html', graph_json=graph_json, total_loss=total_loss)

if __name__ == '__main__':
    # Timer to automatically open the browser after 1 second
    Timer(1, open_browser).start()
    # Set Flask to run without reloader to avoid double execution
    app.run(port=5000, debug=True, use_reloader=False)
