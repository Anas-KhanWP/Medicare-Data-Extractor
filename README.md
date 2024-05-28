# Medicare Data Extractor

## Overview
This Python script allows users to extract data from Medicare.gov using a specified ZIP code. Users can choose to extract data for hospitals, pharmacists, or Medicare plans. This tool is designed to streamline the process of gathering relevant healthcare information based on geographic location.

## Features
- **Data Extraction by ZIP Code**: Extract detailed information from Medicare.gov using a specified ZIP code.
- **Flexible Data Selection**: Choose to extract data for hospitals, pharmacists, or Medicare plans.
- **User-Friendly Interface**: Simple prompts to guide the user through data extraction.

## How It Works
1. **Input the ZIP Code**: Enter the ZIP code for which you want to extract data.
2. **Select Data Type**: Choose whether you want to extract information about hospitals, pharmacists, or Medicare plans.
3. **Execute the Script**: The script will fetch the relevant data from Medicare.gov and display it.

## Installation
To install and set up the Medicare Data Extraction Script, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Anas-KhanWP/Medicare-Data-Extractor.git
    ```
2. Navigate to the project directory:
    ```bash
    cd medicare-data-extractor
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To use the Medicare Data Extraction Script, follow these steps:

1. Launch the script:
    ```bash
    python Extractor.py
    ```
2. When prompted, enter the ZIP code for which you want to extract data.
3. Select the type of data you want to extract:
   - Enter `1` for hospitals
   - Enter `2` for pharmacists
   - Enter `3` for Medicare plans

The script will fetch and display the relevant data from Medicare.gov based on your input.

## Example
To extract hospital data for ZIP code 90210:

1. Run the script:
    ```bash
    python extract_medicare_data.py
    ```
2. Enter `90210` when prompted for the ZIP code.
3. Enter `1` to select hospitals.

The script will display a list of hospitals in the specified ZIP code area.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any questions or issues, please contact us at support@yourdomain.com.

---

Thank you for using the Medicare Data Extraction Script! We hope it significantly enhances your ability to gather healthcare information.
