# 🕵️‍♀️ iCIMS Job Posting Web Scraper

> A powerful automated scraper that extracts comprehensive job posting information from iCIMS-powered career portals using Selenium and BeautifulSoup.

## 📋 Overview

The iCIMS Job Posting Web Scraper automates the collection of job data from dynamic career pages. It intelligently handles JavaScript-rendered content, iframes, and structured JSON-LD metadata to extract detailed job information including titles, company details, locations, employment types, descriptions, and more. All scraped data is exported to a clean JSON file for easy integration with your workflows.

## ✨ Key Features

- **Dynamic Content Handling** – Seamlessly scrapes JavaScript-heavy and iframe-based job pages
- **Structured Data Extraction** – Parses JSON-LD job schema for accurate, standardized results
- **JSON Export** – Saves data in clean, readable JSON format
- **Debug Mode** – Provides detailed step-by-step extraction logs for troubleshooting
- **Headless Operation** – Runs silently in the background without opening browser windows
- **Comprehensive Data Capture** – Extracts job titles, company names, locations, employment types, descriptions, and additional metadata

## 🛠️ Tech Stack

- **Python 3.7+** – Core programming language
- **Selenium** – Handles dynamic, JavaScript-heavy job pages
- **BeautifulSoup4** – Parses and extracts structured HTML content
- **JSON** – Stores scraped job data

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (matching your Chrome version)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/icims-job-scraper.git
   cd icims-job-scraper
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install selenium beautifulsoup4
   ```

5. **Set up ChromeDriver**
   
   Download ChromeDriver that matches your Chrome version from the [official site](https://chromedriver.chromium.org/downloads) and ensure it's accessible in your system PATH.

### Usage

Run the scraper from your terminal:

```bash
python scrape_job.py
```

The scraper will:
- Extract job details from the configured iCIMS URL
- Display extracted data in your terminal
- Save results to `job_posting.json`

## 📂 Project Structure

```
SCRAP/
│
├── scrape_job.py          # Main scraper script
└── job_posting.json       # Output file with scraped data
```

## 📄 Example Output

```json
{
  "url": "https://careers-aeieng.icims.com/jobs/5417/engineering-data-analyst/job",
  "job_id": "5417",
  "job_title": "Engineering Data Analyst",
  "company": "AEI Engineering",
  "location": "Remote, United States",
  "employment_type": "Full-time",
  "description": "The Engineering Data Analyst will be responsible for...",
  "posted_date": "2025-10-06T00:00:00",
  "salary": null,
  "additional_info": {
    "Department": "Data Analytics",
    "Job Category": "Engineering"
  }
}
```

## 🔮 Future Enhancements

- Multi-page job listing scraping
- CSV/Excel/Database export options
- CLI argument support for custom URLs
- Web interface (Flask or FastAPI)
- Rate limiting and retry logic
- Proxy support for large-scale scraping

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always review and comply with a website's Terms of Service and robots.txt before scraping. Use responsibly and ethically.

## 👤 Author

**Nahima Machingal**  
*Engineer | Python Developer | Web Automation Enthusiast*  
October 7, 2025

---

*Made with ❤️ and Python*
