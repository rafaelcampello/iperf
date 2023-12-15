from flask import Flask, render_template, request, redirect, url_for
import re
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
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
    # Verify if the file was sent
    if 'iperf_results_file' not in request.files:
        return redirect(request.url)

    file = request.files['iperf_results_file']
    
    # Verify if a file was selected
    if file.filename == '':
        return redirect(request.url)

    # Verify if the file has an allowed extension.
    if not allowed_file(file.filename):
        return redirect(request.url)

    # Process the results file
    iperf_results = file.read().decode('utf-8')

    # Lists to storage the percentage of loss and time
    loss_percentages = []
    time_seconds = []

    for match in re.finditer(r'(\d+\.\d+)-(\d+\.\d+) sec.*\((\d+)%\)', iperf_results):
        time_start, time_end, loss_percentage = map(float, match.groups())
        time_mid = (time_start + time_end) / 2.0
        loss_percentages.append(loss_percentage)
        time_seconds.append(time_mid)

    # Create a Plotly graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_seconds, y=loss_percentages, mode='lines+markers'))
    fig.update_layout(
        xaxis_title='Time (seconds)',
        yaxis_title='Packet Loss Percentage',
        title='Packet Loss VS Time'
    )

    # Converts the Plotly graph into a base64 image
    img = BytesIO()
    fig.write_image(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.read()).decode()

    return render_template('results.html', graph_url=graph_url)

if __name__ == '__main__':
    app.run()
