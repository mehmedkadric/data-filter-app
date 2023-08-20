# Data Filter App

## About

This repository hosts the "data-filter-app," a tool designed to efficiently filter large datasets (in CSV or Excel formats). Often, there's a need to perform specific queries on these datasets, such as extracting all entries where the City field contains the value "New York" or has the value "Chicago." While web applications might not be optimal for handling substantial datasets like those reaching 20 GB or 200 GB, this app provides a rapid solution. It rapidly filters the data according to your criteria and generates output files in either CSV or XLSX formats.

## Installation Instructions

1. Clone this repository and navigate to the project directory.
2. Create a virtual environment for the app.
3. Install the required dependencies using the command: `pip install -r requirements.txt` (or `pip3 install -r requirements.txt`)
4. Verify the setup by running: `python find_csv2xls_3.py` (or `python3 find_csv2xls_3.py`)

## Optional: Packaging the Application

You have the option to package the application for easy distribution on different platforms.

### Packaging for macOS

1. Install `py2app` by running: `pip install py2app`
2. Execute the command: `python setup.py py2app`. This will create a packaged application (`.app`).
3. The generated application will be located in the `dist` directory within your project folder.

### Packaging for Windows

1. Install `pyinstaller` by running: `pip install pyinstaller`
2. Run the following command: `pyinstaller --onefile find_csv2xls_3.py`. This will create a packaged application (`.exe`).
3. The resulting application will be found in the `dist` directory within your project folder.


## Technologies Used
- Python
- Pandas
- tkinter

The script combines these technologies to create a user-friendly graphical interface for searching and filtering CSV and Excel files based on specified conditions. It leverages pandas for efficient data handling and tkinter for the graphical interface components.
