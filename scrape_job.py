"""
iCIMS Job Posting Web Scraper
================================
Author: [Your Name]
Date: October 6, 2025
Purpose: Scrape job posting details from iCIMS career portals

Description:
    This script uses Selenium WebDriver to scrape job postings from iCIMS-powered
    career websites. It handles dynamic JavaScript content and iframe-based layouts.

Requirements:
    - Python 3.7+
    - selenium - handle dynamic pages
    - beautifulsoup4 - to parse HTML content easily
    
Installation:
    pip install selenium beautifulsoup4

Usage:
    python scrape_job.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime


def setup_chrome_driver():
    """
    Configure and initialize Chrome WebDriver with optimal settings.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
        
    Settings:
        - Headless mode for background execution
        - Custom user agent to avoid bot detection
        - Disabled automation flags for stealth
    """
    chrome_options = Options()
    
    # Run Chrome in headless mode (no GUI)
    chrome_options.add_argument('--headless')
    
    # Security and compatibility settings
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Anti-bot detection measures
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Window and display settings
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Mimic real browser with user agent
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    # Initialize and return driver
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_job_title(driver, debug=True):
    """
    Extract job title from the page using multiple selector strategies.
    
    Args:
        driver: Selenium WebDriver instance
        debug (bool): Enable debug output
        
    Returns:
        str: Job title or None if not found
        
    Strategy:
        Tries multiple CSS selectors in order of reliability
    """
    # List of selectors to try (most specific to most general)
    title_selectors = [
        (By.CSS_SELECTOR, "h1.iCIMS_JobsTable h2"),
        (By.CSS_SELECTOR, ".iCIMS_Header"),
        (By.CSS_SELECTOR, "h1"),
        (By.CSS_SELECTOR, "h2.iCIMS_InfoMsg_Job"),
        (By.XPATH, "//div[@class='iCIMS_JobsTable']//h2")
    ]
    
    for by, selector in title_selectors:
        try:
            element = driver.find_element(by, selector)
            if element and element.text.strip():
                title = element.text.strip()
                if debug:
                    print(f"✓ Job Title found: {title}")
                return title
        except Exception as e:
            if debug:
                print(f"  Selector '{selector}' failed: {str(e)[:50]}")
            continue
    
    if debug:
        print("✗ Job title not found")
    return None


def extract_location(driver, debug=True):
    """
    Extract job location from definition list elements.
    
    Args:
        driver: Selenium WebDriver instance
        debug (bool): Enable debug output
        
    Returns:
        str: Location or None if not found
        
    Logic:
        Looks for <dd> elements containing comma or 'Remote'
    """
    try:
        location_elements = driver.find_elements(By.CSS_SELECTOR, "dd")
        for elem in location_elements:
            text = elem.text.strip()
            # Location typically contains comma or 'Remote'
            if ',' in text or 'Remote' in text.lower():
                if debug:
                    print(f"✓ Location found: {text}")
                return text
    except Exception as e:
        if debug:
            print(f"✗ Location extraction failed: {str(e)}")
    
    return None


def extract_definition_lists(driver, debug=True):
    """
    Extract key-value pairs from HTML definition lists (dl/dt/dd).
    
    Args:
        driver: Selenium WebDriver instance
        debug (bool): Enable debug output
        
    Returns:
        dict: Dictionary of extracted fields
        
    HTML Structure:
        <dl>
            <dt>Field Name:</dt>
            <dd>Field Value</dd>
        </dl>
    """
    additional_info = {}
    
    try:
        # Find all definition lists on the page
        dls = driver.find_elements(By.TAG_NAME, "dl")
        
        for dl in dls:
            # Get all terms (labels) and descriptions (values)
            dts = dl.find_elements(By.TAG_NAME, "dt")
            dds = dl.find_elements(By.TAG_NAME, "dd")
            
            # Pair them together
            for dt, dd in zip(dts, dds):
                key = dt.text.strip()
                value = dd.text.strip()
                
                if key and value:
                    additional_info[key] = value
                    if debug:
                        print(f"✓ Field extracted: {key} = {value}")
        
    except Exception as e:
        if debug:
            print(f"✗ Definition list extraction failed: {str(e)}")
    
    return additional_info


def extract_description(driver, debug=True):
    """
    Extract full job description text.
    
    Args:
        driver: Selenium WebDriver instance
        debug (bool): Enable debug output
        
    Returns:
        str: Job description or None if not found
        
    Strategy:
        Tries multiple selectors for description containers
    """
    desc_selectors = [
        ".iCIMS_InfoMsg.iCIMS_InfoField_Job",
        ".iCIMS_JobContent",
        "div[class*='JobDescription']",
        "div.iCIMS_Expandable_Container"
    ]
    
    for selector in desc_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                # Description should be substantial
                if len(text) > 100:
                    if debug:
                        print(f"✓ Description found ({len(text)} characters)")
                    return text
        except Exception as e:
            if debug:
                print(f"  Selector '{selector}' failed: {str(e)[:50]}")
            continue
    
    if debug:
        print("✗ Description not found")
    return None


def extract_json_ld(soup, debug=True):
    """
    Extract structured data from JSON-LD schema markup.
    
    Args:
        soup: BeautifulSoup object of the page
        debug (bool): Enable debug output
        
    Returns:
        dict: Structured job data or empty dict
        
    About JSON-LD:
        JSON-LD is a structured data format used by search engines.
        It contains standardized job posting information.
    """
    structured_data = {}
    
    try:
        # Find all JSON-LD script tags
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Check if this is a JobPosting schema
                if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                    structured_data['title'] = data.get('title')
                    structured_data['company'] = data.get('hiringOrganization', {}).get('name')
                    structured_data['description'] = data.get('description')
                    structured_data['posted_date'] = data.get('datePosted')
                    structured_data['employment_type'] = data.get('employmentType')
                    
                    # Extract location from address
                    location_data = data.get('jobLocation', {})
                    if isinstance(location_data, dict):
                        address = location_data.get('address', {})
                        city = address.get('addressLocality', '')
                        state = address.get('addressRegion', '')
                        structured_data['location'] = f"{city}, {state}".strip(', ')
                    
                    # Extract salary if available
                    salary_info = data.get('baseSalary', {})
                    if salary_info:
                        structured_data['salary'] = str(salary_info)
                    
                    if debug:
                        print(f"✓ JSON-LD data extracted successfully")
                    break
                    
            except json.JSONDecodeError as e:
                if debug:
                    print(f"  JSON parsing failed: {str(e)}")
                continue
                
    except Exception as e:
        if debug:
            print(f"✗ JSON-LD extraction failed: {str(e)}")
    
    return structured_data


def scrape_icims_job(url, debug=True):
    """
    Main function to scrape job posting from iCIMS career portal.
    
    Args:
        url (str): Full URL of the job posting
        debug (bool): Enable detailed logging
        
    Returns:
        dict: Complete job data or None if failed
        
    Process:
        1. Initialize Chrome driver
        2. Load the page
        3. Switch to iframe (iCIMS content is in iframe)
        4. Extract all job details
        5. Return structured data
    """
    driver = None
    
    try:
        # Step 1: Initialize browser
        if debug:
            print("\n" + "="*70)
            print("STEP 1: Initializing Chrome WebDriver")
            print("="*70)
        
        driver = setup_chrome_driver()
        
        # Step 2: Load the page
        if debug:
            print("\n" + "="*70)
            print("STEP 2: Loading Job Posting Page")
            print("="*70)
            print(f"URL: {url}")
        
        driver.get(url)
        
        # Step 3: Wait for and switch to iframe
        if debug:
            print("\n" + "="*70)
            print("STEP 3: Locating and Switching to iFrame")
            print("="*70)
            print("iCIMS uses iframes to embed job content...")
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for iframe to be present
        iframe = wait.until(
            EC.presence_of_element_located((By.ID, "icims_content_iframe"))
        )
        
        if debug:
            print("✓ iFrame found: icims_content_iframe")
        
        # CRITICAL: Switch to iframe context
        driver.switch_to.frame(iframe)
        
        if debug:
            print("✓ Switched to iframe - now accessing job content")
        
        # Wait for content to load
        time.sleep(3)
        
        # Step 4: Extract job data
        if debug:
            print("\n" + "="*70)
            print("STEP 4: Extracting Job Details")
            print("="*70)
        
        # Initialize data structure
        job_data = {
            'url': url,
            'scrape_timestamp': datetime.now().isoformat(),
            'job_id': None,
            'job_title': None,
            'company': None,
            'location': None,
            'description': None,
            'posted_date': None,
            'employment_type': None,
            'additional_info': {},
            'salary': None
        }
        
        # Extract job ID from URL
        if '/jobs/' in url:
            job_data['job_id'] = url.split('/jobs/')[1].split('/')[0]
            if debug:
                print(f"✓ Job ID: {job_data['job_id']}")
        
        # Get page source for BeautifulSoup parsing
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract job title
        job_data['job_title'] = extract_job_title(driver, debug)
        
        # Extract location
        job_data['location'] = extract_location(driver, debug)
        
        # Extract additional fields from definition lists
        job_data['additional_info'] = extract_definition_lists(driver, debug)
        
        # Extract job description
        job_data['description'] = extract_description(driver, debug)
        
        # Extract JSON-LD structured data
        if debug:
            print("\n" + "-"*70)
            print("Extracting JSON-LD Structured Data")
            print("-"*70)
        
        json_ld_data = extract_json_ld(soup, debug)
        
        # Merge JSON-LD data (fill in missing fields)
        if json_ld_data:
            for key, value in json_ld_data.items():
                if value and not job_data.get(key):
                    job_data[key] = value
        
        # Extract full page text as backup
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            job_data['full_page_text'] = body.text
        except:
            pass
        
        if debug:
            print("\n" + "="*70)
            print("✓ EXTRACTION COMPLETE")
            print("="*70)
        
        return job_data
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # Always close the browser
        if driver:
            driver.quit()
            if debug:
                print("\n✓ Browser closed")


def save_to_json(data, filename='job_posting.json'):
    """
    Save scraped data to JSON file.
    
    Args:
        data (dict): Job data to save
        filename (str): Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Data saved to '{filename}'")
        return True
    except Exception as e:
        print(f"\n✗ Failed to save file: {str(e)}")
        return False


def display_results(job_data):
    """
    Display scraped results in a formatted manner.
    
    Args:
        job_data (dict): Scraped job data
    """
    print("\n" + "="*70)
    print("SCRAPED JOB DETAILS")
    print("="*70)
    
    if job_data.get('job_title'):
        print(f"\n📋 Job Title: {job_data['job_title']}")
    
    if job_data.get('company'):
        print(f"🏢 Company: {job_data['company']}")
    
    if job_data.get('location'):
        print(f"📍 Location: {job_data['location']}")
    
    if job_data.get('job_id'):
        print(f"🆔 Job ID: {job_data['job_id']}")
    
    if job_data.get('posted_date'):
        print(f"📅 Posted Date: {job_data['posted_date']}")
    
    if job_data.get('employment_type'):
        print(f"💼 Employment Type: {job_data['employment_type']}")
    
    if job_data.get('salary'):
        print(f"💰 Salary: {job_data['salary']}")
    
    # Display additional info
    if job_data.get('additional_info'):
        print(f"\n📝 Additional Information:")
        for key, value in job_data['additional_info'].items():
            print(f"   • {key}: {value}")
    
    # Display description preview
    if job_data.get('description'):
        desc = job_data['description']
        print(f"\n📄 Job Description ({len(desc)} characters):")
        print(f"   {desc[:400]}...")
        if len(desc) > 400:
            print(f"   [Truncated - Full description in JSON file]")
    
    print("\n" + "="*70)


def main():
    """
    Main execution function.
    """
    # Job posting URL
    url = "https://careers-aeieng.icims.com/jobs/5417/engineering-data-analyst/job?mobile=false&width=1920&height=500&bga=true&needsRedirect=false&jan1offset=330&jun1offset=330"
    
    print("="*70)
    print("iCIMS JOB POSTING WEB SCRAPER")
    print("="*70)
    print(f"Target: Engineering Data Analyst Position")
    print(f"Platform: iCIMS Career Portal")
    print("="*70)
    
    # Scrape the job
    job_data = scrape_icims_job(url, debug=True)
    
    if job_data:
        # Display results
        display_results(job_data)
        
        # Save to JSON
        save_to_json(job_data, 'job_posting.json')
        
        print("\n✅ Scraping completed successfully!")
    else:
        print("\n❌ Scraping failed. Please check the error messages above.")


if __name__ == "__main__":
    main()