from flask import Flask, render_template, request, redirect, url_for
import re
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_results():
    if 'iperf_results_file' not in request.files:
        return redirect(request.url)
    file = request.files['iperf_results_file']
    if file.filename == '':
        return redirect(request.url)
    if not allowed_file(file.filename):
        return redirect(request.url)

    iperf_results = file.read().decode('utf-8')

    loss_percentages = []
    timestamps = []

    # Regex updated to match the timestamp at the beginning of each line
    for match in re.finditer(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(\d+\.\d+)-(\d+\.\d+) sec.*\((\d+)%\)', iperf_results):
        timestamp_str, time_start, time_end, loss_percentage = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        timestamps.append(timestamp)  # Using the start time of each interval
        loss_percentages.append(float(loss_percentage))

    # Extract the total packet loss percentage
    total_loss_match = re.search(r'\d+/\d+\s+\((\d+)%\)', iperf_results)
    if total_loss_match:
        total_loss_percentage = total_loss_match.group(1)
    else:
        total_loss_percentage = "N/A"

    # Create a Plotly graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=loss_percentages, mode='lines+markers'))
    fig.update_layout(
        xaxis_title='Time',
        xaxis=dict(
            tickformat='%H:%M:%S',  # Format the x-axis labels to show time
        ),
        yaxis_title='Packet Loss Percentage',
        title=f'Packet Loss Over Time (Total Loss: {total_loss_percentage}%)'
    )

    # Converts the Plotly graph into a base64 image
    img = BytesIO()
    fig.write_image(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.read()).decode()

    return render_template('results.html', graph_url=graph_url, total_loss=total_loss_percentage)

if __name__ == '__main__':
    app.run(debug=True)
