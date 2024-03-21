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
        # Find total loss percentage
        # Extrair a perda total de pacotes do último resultado que contém a perda total
    total_loss_match = re.search(r'\((\d+\.\d+)%\)', iperf_results.splitlines()[-1])
    if total_loss_match:
        total_loss = total_loss_match.group(1) + "%"
    else:
        # Se não encontrar uma correspondência, isso significa que a perda pode ser 0%
        # ou o arquivo pode não seguir o formato esperado.
        # Assumiremos 0% para manter o comportamento consistente.
        total_loss = "0%"
        
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
            hovermode='closest'
        )

        graph_json = fig.to_json()
    else:
        graph_json = None

    return render_template('results.html', graph_json=graph_json, total_loss=total_loss)

if __name__ == '__main__':
    app.run(debug=True)
