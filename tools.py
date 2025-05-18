import logging
import subprocess
import sys
import time
import urllib.parse

# Import multiple webdriver options to try different approaches
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def kill_browser_processes():
    """Kill all browser and webdriver processes"""
    try:
        logger.info("Attempting to kill browser processes")
        if sys.platform.startswith("linux"):
            # Kill Firefox, Chrome, PhantomJS and their drivers
            subprocess.run(
                ["pkill", "-9", "-f", "firefox|chrome|phantom"], stderr=subprocess.PIPE
            )
            subprocess.run(
                ["pkill", "-9", "-f", "geckodriver|chromedriver|phantomjs"],
                stderr=subprocess.PIPE,
            )
        elif sys.platform == "darwin":
            subprocess.run(
                ["pkill", "-9", "-f", "firefox|Google Chrome|phantom"],
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["pkill", "-9", "-f", "geckodriver|chromedriver|phantomjs"],
                stderr=subprocess.PIPE,
            )
        elif sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/f", "/im", "firefox.exe"], stderr=subprocess.PIPE
            )
            subprocess.run(
                ["taskkill", "/f", "/im", "chrome.exe"], stderr=subprocess.PIPE
            )
            subprocess.run(
                ["taskkill", "/f", "/im", "phantomjs.exe"], stderr=subprocess.PIPE
            )
            subprocess.run(
                ["taskkill", "/f", "/im", "geckodriver.exe"], stderr=subprocess.PIPE
            )
            subprocess.run(
                ["taskkill", "/f", "/im", "chromedriver.exe"], stderr=subprocess.PIPE
            )
        logger.info("Browser processes killed")
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Error killing browser processes: {e}")


def create_simple_driver():
    """Create a minimal browser driver that works in containerized environments"""

    # Kill any existing browser processes
    kill_browser_processes()

    drivers_to_try = []

    # 1. Try headless Chrome with minimal options (most compatible)
    try:
        logger.info("Attempting to create headless Chrome driver")
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # Add Chrome to drivers to try
        drivers_to_try.append(("chrome", chrome_options))
    except Exception as e:
        logger.warning(f"Error setting up Chrome options: {e}")

    # 2. Try Firefox
    try:
        logger.info("Setting up Firefox options")
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")

        # Add Firefox to drivers to try
        drivers_to_try.append(("firefox", firefox_options))
    except Exception as e:
        logger.warning(f"Error setting up Firefox options: {e}")

    # Try each driver type
    for driver_name, options in drivers_to_try:
        try:
            logger.info(f"Attempting to initialize {driver_name} driver")

            if driver_name == "chrome":
                driver = webdriver.Chrome(options=options)
            elif driver_name == "firefox":
                driver = webdriver.Firefox(options=options)

            # Test driver with a simple command
            logger.info(f"Testing {driver_name} driver")
            current_url = driver.current_url
            logger.info(
                f"Successfully created {driver_name} driver. Current URL: {current_url}"
            )

            # Set short timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(20)

            return driver, driver_name

        except Exception as e:
            logger.error(f"Failed to initialize {driver_name} driver: {e}")
            # Clean up if driver was partially created
            try:
                if "driver" in locals() and driver:
                    driver.quit()
            except:
                pass

            # Kill processes before trying next driver
            kill_browser_processes()

    # If we got here, all driver attempts failed
    logger.error("All driver initialization attempts failed")
    return None, None


def get_all_coniverse_courses(
    search_term: str = "", max_courses=settings.MAX_COURSES
) -> list:
    driver = None
    driver_name = None

    try:
        logger.info(f"Starting course search for: {search_term}")

        # Create a minimal driver that works
        driver, driver_name = create_simple_driver()

        if not driver:
            return ["Error: Failed to create any browser driver"]

        logger.info(f"Successfully created {driver_name} driver")

        # Now use the driver for the actual task
        encoded_search_term = urllib.parse.quote_plus(search_term)
        url = f"https://coniverse.com/search/learning/courses?search={encoded_search_term}&ordering=relevance"

        logger.info(f"Navigating to URL: {url}")

        try:
            driver.get(url)
            logger.info("Page requested successfully")
        except TimeoutException:
            logger.warning("Page load timed out. Trying to continue anyway...")
            try:
                driver.execute_script("window.stop();")
            except Exception as e:
                logger.error(f"Failed to stop page load: {e}")
        except Exception as e:
            logger.error(f"Error loading page: {e}")
            return [f"Error loading page: {str(e)}"]

        # Log some debug info
        logger.info(f"Current page title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")

        # Take a screenshot for debugging
        try:
            screenshot_path = f"/tmp/coniverse_search_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            logger.warning(f"Failed to save screenshot: {e}")

        # Wait for page to load
        logger.info("Waiting for page to load...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Page body loaded")

            # Wait for JavaScript content
            time.sleep(5)
        except Exception as e:
            logger.warning(f"Timeout waiting for page: {e}")

        # Extract course titles using multiple methods
        course_titles = []

        # Try different selectors
        selectors_to_try = [
            'span[data-qa="txt-name"]',
            ".txt-name",
            ".card-content span",
            ".search-result-card span",
            'div[id="search-courses-page"] span',
            ".course-card .title",
            ".course-title",
            "h3.course-name",
            ".course-list .item-title",
            'a[href*="/course/"] .title',
            # More general selectors
            ".card h3",
            "h3",
            ".card span",
        ]

        elements_found = False
        for selector in selectors_to_try:
            try:
                logger.info(f"Trying selector: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"Found {len(elements)} elements with selector {selector}")

                for element in elements:
                    try:
                        title_text = element.text.strip()
                        if (
                            title_text
                            and len(title_text) > 5
                            and title_text.lower()
                            not in [
                                "coniverse",
                                "results",
                                "filters",
                                "search",
                                "course",
                            ]
                            and title_text not in course_titles
                        ):
                            course_titles.append(title_text)
                            elements_found = True
                            logger.info(f"Added course title: {title_text}")
                    except Exception:
                        continue

                if elements_found:
                    logger.info(f"Successfully found courses with selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")

        # Return results
        if course_titles:
            final_courses = course_titles[:max_courses]
            logger.info(f"Returning {len(final_courses)} courses")
            return final_courses
        else:
            logger.warning("No courses found")
            return ["No courses found."]

    except Exception as e:
        logger.error(f"Error in get_all_coniverse_courses: {e}")
        return [f"Error retrieving courses: {str(e)}"]

    finally:
        # Clean up browser driver
        if driver:
            try:
                logger.info(f"Closing {driver_name} driver")
                driver.quit()
                logger.info(f"{driver_name} driver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing {driver_name} driver: {e}")

        # Kill any remaining browser processes
        kill_browser_processes()
