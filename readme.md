# Email Scraper

This is an educational email scraping tool built using Python, Flet, and other libraries. By providing a domain extension (such as .com, .ch, or .fr), it searches Google for URLs, fetches their content, finds email addresses, removes duplicates, and displays progress in a simple user interface.

## Features

- Search Google for URLs containing specific domain extensions.  
- Extract and display discovered email addresses in real time.  
- Remove duplicate entries automatically.  
- Simple GUI built with **Flet**.  
- Clear and concise logs for each step of the scraping process.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Foolian2/email-scraper.git
   cd email-scraper
   ```
2. **Create a virtual environment (optional)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements

- Python 3.7 or higher  
- flet for the GUI  
- requests for making HTTP requests  
- googlesearch-python for performing Google searches  
- re for regex-based email extraction  

## License

This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.

## Disclaimer

This tool is provided **for educational purposes only**. Use it responsibly and comply with all applicable laws and regulations.
