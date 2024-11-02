
# iPerf Plotting App

This is a Flask-based web application for visualizing packet loss data from iPerf test results. The app parses iPerf output files and displays packet loss over time in an interactive Plotly graph.

## Features

- **Automated Parsing**: Reads and parses iPerf output files to extract timestamp and packet loss data.
- **Interactive Plotting**: Plots packet loss over time using Plotly, allowing users to visualize network stability.
- **Loss Summary**: Provides a summary of total packet loss as a percentage.
- **Automatic Browser Launch**: Opens the app in the web browser automatically.

## Requirements

- **Python 3.7+**
- **Flask** for web development
- **Plotly** for data visualization
- **PyInstaller** (for building the standalone executable)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/rafaelcampello/iperf
cd iperf
```

### 2. Create and Activate a Virtual Environment

To avoid package conflicts, create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

- **On Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

## Running the App

To start the app for development, run:

```bash
python app.py
```

This will launch the Flask server, and the app will open automatically in your web browser at `http://127.0.0.1:5000/`.

## Building the Executable

To create a standalone executable for distribution, you can use PyInstaller. Run the following command in the virtual environment:

```bash
pyinstaller --onefile --icon=iperf.ico --add-data "templates;templates" --add-data "static;static" app.py
```

This will generate an executable file in the `dist` folder. You can distribute this file to users who don't have Python installed. Note that the executable may take a few minutes to run on systems with strict security policies.

## Usage

1. **Upload iPerf File**: On the app's main page, upload an iPerf result file. The app supports files with timestamps and basic packet loss format.
2. **View Graph**: After uploading, the app will display an interactive graph showing packet loss over time.
3. **Review Summary**: A summary of the total packet loss percentage will be displayed below the graph.

## File Formats Supported

- **With Timestamps**: e.g., `2024-08-01 12:00:00 10.0-20.0 sec 0.1%`
- **Without Timestamps**: e.g., `[ID] 0.0-10.0 sec 0.0%`

The app automatically detects the format and processes the data accordingly.

## Troubleshooting

- **Executable Blocked on Company Devices**: If the executable doesn't run immediately on company devices, wait a few minutes. Security processes may take some time to approve the application.
- **Duplicate Browser Windows**: If the browser opens twice, ensure there are no duplicate calls to `webbrowser.open` in the code.
- **Permission Errors**: If you encounter file access errors, try running the executable as an administrator or check folder permissions.

## Code Overview

- **app.py**: The main application file with all routes and logic.
- **templates/**: Contains HTML templates (`index.html` and `results.html`).
- **static/**: Folder for static assets like CSS, JavaScript, and icons.

## Example iPerf File Format

```text
2024-08-01 12:00:00 10.0-20.0 sec 0.1%
2024-08-01 12:00:10 20.0-30.0 sec 0.2%
...
```

## Contributing

Contributions are welcome! Please fork the repository and create a pull request for any bug fixes or feature enhancements.

## About the Author

This iPerf plotting application was developed by Rafael Campello https://github.com/rafaelcampello https://www.linkedin.com/in/rafaelbcampelloeng/.
