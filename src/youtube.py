import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import logging
from urllib.parse import unquote
import re
import tkinter as tk
from tkinter import messagebox

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- List of African countries for filtering ---
AFRICAN_COUNTRIES = {
    'algeria', 'angola', 'benin', 'botswana', 'burkina faso', 'burundi', 'cabo verde', 'cameroon',
    'central african republic', 'chad', 'comoros', 'congo, democratic republic of the',
    'congo, republic of the', "cote d'ivoire", 'djibouti', 'egypt', 'equatorial guinea', 'eritrea',
    'eswatini', 'ethiopia', 'gabon', 'gambia', 'ghana', 'guinea', 'guinea-bissau', 'kenya',
    'lesotho', 'liberia', 'libya', 'madagascar', 'malawi', 'mali', 'mauritania', 'mauritius',
    'morocco', 'mozambique', 'namibia', 'niger', 'rwanda', 'sao tome and principe',
    'senegal', 'seychelles', 'sierra leone', 'somalia', 'south africa', 'south sudan', 'sudan',
    'tanzania', 'togo', 'tunisia', 'uganda', 'zambia', 'zimbabwe'
}


class YouTubeChannelScraper:
    def __init__(self, headless=False):
        self.driver = self._setup_driver(headless)
        self.existing_channels = set()
        # --- NEW: Set for check.txt URLs ---
        self.processed_urls_from_check_txt = set()

    def _setup_driver(self, headless):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1920,1080')

        # This preference allows images to load
        prefs = {
            "profile.managed_default_content_settings.plugins": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        return webdriver.Chrome(options=chrome_options)

    # --- Pop-up 1: Confirmation to Scrape ---
    def _ask_to_scrape(self, channel_identifier, timeout=10):
        """Creates a Tkinter dialog asking for user confirmation with a timeout."""
        root = tk.Tk()
        root.withdraw()

        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - 175
        y = (screen_height // 2) - 50

        answer = None

        def on_yes():
            nonlocal answer
            answer = True
            popup.destroy()

        def on_no():
            nonlocal answer
            answer = False
            popup.destroy()

        def on_timeout():
            if popup.winfo_exists():
                logger.warning("Confirmation timed out. Defaulting to 'No'.")
                on_no()

        popup = tk.Toplevel(root)
        popup.title("Scrape Confirmation")
        popup.geometry(f'350x100+{x}+{y}')
        popup.attributes('-topmost', True)

        label_text = f"Proceed with scraping '{channel_identifier}'?"
        label = tk.Label(popup, text=label_text, wraplength=330)
        label.pack(pady=10)

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=5)

        yes_button = tk.Button(button_frame, text="Yes, Scrape", command=on_yes, width=15)
        yes_button.pack(side=tk.LEFT, padx=10)

        no_button = tk.Button(button_frame, text="No, Skip", command=on_no, width=15)
        no_button.pack(side=tk.RIGHT, padx=10)

        popup.after(timeout * 1000, on_timeout)
        popup.wait_window()

        try:
            root.destroy()
        except tk.TclError:
            pass
        return answer
        
    # --- NEW: Pop-up 2: Niche Selection ---
    def _ask_for_niche(self, channel_identifier, timeout=12):
        """Creates a Tkinter dialog for selecting a niche with a timeout."""
        root = tk.Tk()
        root.withdraw()

        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - 200
        y = (screen_height // 2) - 75

        selected_niche = "N/A"  # Default value

        def set_niche(niche):
            nonlocal selected_niche
            selected_niche = niche
            popup.destroy()

        def on_timeout():
            if popup.winfo_exists():
                logger.warning("Niche selection timed out. Defaulting to 'N/A'.")
                popup.destroy()

        popup = tk.Toplevel(root)
        popup.title("Select Niche")
        popup.geometry(f'400x150+{x}+{y}') # Made window larger for longer text
        popup.attributes('-topmost', True)

        label = tk.Label(popup, text=f"Select a niche for '{channel_identifier}':", wraplength=380)
        label.pack(pady=10)
        
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=5, fill='x')

        # Create buttons for each niche
        niche1_button = tk.Button(button_frame, text="How to grow on Social Media", command=lambda: set_niche("How to grow on Social Media"))
        niche1_button.pack(fill='x', padx=20, pady=2)

        niche2_button = tk.Button(button_frame, text="AI", command=lambda: set_niche("AI"))
        niche2_button.pack(fill='x', padx=20, pady=2)

        niche3_button = tk.Button(button_frame, text="Video editing", command=lambda: set_niche("Video editing"))
        niche3_button.pack(fill='x', padx=20, pady=2)

        popup.after(timeout * 1000, on_timeout)
        popup.wait_window()

        try:
            root.destroy()
        except tk.TclError:
            pass
        return selected_niche


    def parse_username_to_url(self, username):
        username = username.strip().lstrip('@')
        return f"https://www.youtube.com/@{username}"

    def load_existing_data(self, csv_file):
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                if 'YouTube Channel Link' in df.columns:
                    self.existing_channels = set(df['YouTube Channel Link'].dropna())
                    logger.info(f"Loaded {len(self.existing_channels)} existing channels from {csv_file}")
            except Exception as e:
                logger.error(f"Error loading existing data: {e}")

    # --- NEW: Method to load URLs from check.txt ---
    def _load_processed_urls(self, check_file):
        if os.path.exists(check_file):
            try:
                with open(check_file, 'r', encoding='utf-8') as f:
                    # Read URLs, strip whitespace, and filter out empty lines
                    self.processed_urls_from_check_txt = set(line.strip() for line in f if line.strip())
                logger.info(f"Loaded {len(self.processed_urls_from_check_txt)} processed URLs from {check_file}")
            except Exception as e:
                logger.error(f"Error loading processed URLs from {check_file}: {e}")

    # --- Data Extraction Methods (Unchanged) ---
    def extract_channel_name(self):
        try:
            name = self.driver.find_element(By.XPATH,"//ytd-engagement-panel-title-header-renderer//yt-formatted-string[@id='title-text']").text.strip()
            if name: return name
        except NoSuchElementException: pass
        try:
            name = self.driver.find_element(By.XPATH, "//div[@id='channel-header']//yt-formatted-string[@id='text']").text.strip()
            if name: return name
        except NoSuchElementException: pass
        try:
            name = self.driver.find_element(By.ID, "title-text").text.strip()
            if name: return name
        except NoSuchElementException:
            logger.error("Could not extract channel name using any method.")
            return "N/A"
        logger.warning("A potential channel name element was found, but it was empty.")
        return "N/A"

    def extract_subscribers(self):
        try:
            return self.driver.find_element(By.ID, "subscriber-count").text.strip()
        except NoSuchElementException:
            try:
                return self.driver.find_element(By.XPATH, "//td[contains(., 'subscribers')]").text.strip()
            except NoSuchElementException:
                logger.warning("Could not find subscriber count.")
                return "N/A"

    def extract_other_links(self):
        try:
            link_elements = self.driver.find_elements(By.XPATH, "//div[@id='links-container']//a")
            if not link_elements:
                link_elements = self.driver.find_elements(By.XPATH,"//div[contains(@class, 'ytChannelExternalLinkViewModelContainer')]//a")
        except NoSuchElementException:
            return "N/A"

        links = []
        for element in link_elements:
            href = element.get_attribute('href')
            if href:
                if 'youtube.com/redirect?' in href:
                    try:
                        from urllib.parse import urlparse, parse_qs
                        parsed = urlparse(href)
                        clean_url = parse_qs(parsed.query).get('q', [href])[0]
                    except:
                        clean_url = href
                else:
                    clean_url = href
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(clean_url).netloc.replace('www.', '')
                    if domain:
                        links.append(f'=HYPERLINK("{clean_url}","{domain}")')
                    else:
                        links.append(clean_url)
                except:
                    links.append(clean_url)
        return "; ".join(links) if links else "N/A"

    def extract_country(self):
        try:
            return self.driver.find_element(By.XPATH,"//div[@id='details-container']//span[contains(., 'Location:')]/following-sibling::span").text.strip()
        except NoSuchElementException:
            try:
                country_element = self.driver.find_element(By.XPATH, "//tr[.//yt-icon[@icon='privacy_public']]/td[2]")
                country_text = country_element.text.strip()
                if country_text and len(country_text) > 1: return country_text
            except NoSuchElementException: pass
            try:
                country_element = self.driver.find_element(By.XPATH,"//tr[.//svg[contains(@viewBox, '0 0 24 24')]//path[contains(@d, 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10')]]/td[2]")
                country_text = country_element.text.strip()
                if country_text and len(country_text) > 1: return country_text
            except NoSuchElementException: pass
            try:
                td_elements = self.driver.find_elements(By.XPATH, "//td[@class='style-scope ytd-about-channel-renderer']")
                filter_keywords = ['subscriber', 'video', 'view', 'joined', 'http', '.com', '.org', '.net', 'sign in','email', 'www.youtube.com']
                for element in td_elements:
                    text = element.text.strip()
                    text_lower = text.lower()
                    if (text and len(text) > 1 and len(text) < 50 and
                            not any(char.isdigit() for char in text) and
                            not any(keyword in text_lower for keyword in filter_keywords) and
                            not text_lower.startswith('@') and
                            not '/' in text and not '.' in text):
                        return text
            except NoSuchElementException: pass
            return "United States"

    def extract_description(self):
        try:
            description_text = self.driver.find_element(By.ID, "description-container").text.strip()
        except NoSuchElementException:
            try:
                description_text = self.driver.find_element(By.XPATH,"//span[contains(@class, 'yt-core-attributed-string--white-space-pre-wrap')]").text.strip()
            except NoSuchElementException:
                return "N/A"
        return description_text.replace('\n', ' ').replace('\r', ' ')

    def extract_email_from_description(self, description):
        if not description or description == "N/A":
            return "N/A"
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_regex, description)
        return emails[0] if emails else "N/A"

    def _parse_subscribers(self, sub_string):
        if not sub_string or sub_string == "N/A":
            return None
        try:
            sub_string = sub_string.lower().replace('subscribers', '').strip()
            multiplier = 1
            if 'k' in sub_string:
                num_part = sub_string.replace('k', '')
                multiplier = 1000
            elif 'm' in sub_string:
                num_part = sub_string.replace('m', '')
                multiplier = 1_000_000
            else:
                num_part = sub_string
            return int(float(num_part) * multiplier)
        except (ValueError, TypeError):
            return None

    # --- MODIFIED: Added check for check.txt ---
    def scrape_channel(self, username):
        logger.info(f"--- Starting process for: {username} ---")
        url = self.parse_username_to_url(username)

        # --- NEW CHECK: Check against check.txt file first ---
        if url in self.processed_urls_from_check_txt:
            logger.info(f"Channel {url} found in processed file (check.txt). Skipping.")
            return None # Return None to skip

        # --- EXISTING CHECK: Check against output CSV ---
        if url in self.existing_channels:
            logger.info(f"Channel {url} already exists in the file. Skipping.")
            return None

        try:
            about_url = f"{url.rstrip('/')}/about"
            logger.info(f"Navigating to about page for manual review: {about_url}")
            self.driver.get(about_url)
            time.sleep(3)
        except Exception as e:
            logger.error(f"Failed to navigate to {username}'s about page: {e}")
            raise e

        logger.info("Waiting for user confirmation to scrape...")
        
        prelim_channel_identifier = username
        try:
            name_element = self.driver.find_element(By.XPATH, "//div[@id='channel-header']//yt-formatted-string[@id='text']")
            if name_element and name_element.text.strip():
                prelim_channel_identifier = name_element.text.strip()
        except Exception:
            pass

        should_scrape = self._ask_to_scrape(prelim_channel_identifier, timeout=10)

        if not should_scrape:
            logger.info(f"User chose to skip or timed out for '{username}'. Moving to the next channel.")
            return None

        logger.info(f"User confirmed scrape. Now asking for niche.")
        
        # --- NEW: Call the niche selection pop-up ---
        selected_niche = self._ask_for_niche(prelim_channel_identifier, timeout=12)

        logger.info(f"Niche selected: '{selected_niche}'. Proceeding with full scrape.")
        
        description = self.extract_description()
        channel_data = {
            'Influencer Channel Name': self.extract_channel_name(),
            'YouTube Channel Link': url,
            'Subscribers': self.extract_subscribers(),
            'Other Social Links': self.extract_other_links(),
            'Description': description,
            'Country': self.extract_country(),
            'Email': self.extract_email_from_description(description),
            'Niche': selected_niche  # Add the niche to the data
            
        }

        if channel_data.get('Influencer Channel Name') and channel_data['Influencer Channel Name'] != "N/A":
            logger.info(f"Successfully scraped: {channel_data['Influencer Channel Name']}")
        else:
            logger.error(f"Failed to scrape key data for {username}, check selectors.")

        return channel_data

    def read_usernames_from_file(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]

    def append_to_csv(self, data, file_path):
        # --- MODIFIED: Added 'Niche' to the column order ---
        column_order = ['Influencer Channel Name', 'YouTube Channel Link', 'Subscribers', 'Other Social Links',
                        'Description', 'Country', 'Email', 'Niche']
        df = pd.DataFrame([data], columns=column_order)
        try:
            file_exists = os.path.exists(file_path)
            df.to_csv(file_path, mode='a', header=not file_exists, index=False)
            logger.info(f"Appended data for '{data.get('Influencer Channel Name', 'N/A')}' to {file_path}")
        except Exception as e:
            logger.error(f"Error appending to CSV: {e}")

    # --- NEW: Method to append a URL to check.txt ---
    def _append_url_to_check_file(self, url, check_file):
        """Appends a URL to the check file and adds it to the in-memory set."""
        try:
            with open(check_file, 'a', encoding='utf-8') as f:
                f.write(f"{url}\n")
            # Also update the in-memory set to prevent re-adding in the same session
            self.processed_urls_from_check_txt.add(url)
        except Exception as e:
            logger.error(f"Error appending URL to {check_file}: {e}")

    # --- MODIFIED: To load/use check.txt ---
    def run_scraper(self, usernames_file, output_file, check_file):
        try:
            usernames = self.read_usernames_from_file(usernames_file)
            if not usernames:
                logger.warning(f"{usernames_file} is empty or not found.")
                return
            
            # Load both existing data sources
            self.load_existing_data(output_file)
            self._load_processed_urls(check_file) # <<< NEW

            for username in usernames:
                # Get the URL *before* the try block, so we can add it in 'finally'
                processed_url = self.parse_username_to_url(username)
                
                try:
                    # scrape_channel will now skip if URL is in either set
                    data = self.scrape_channel(username)
                    if data:
                        self.append_to_csv(data, output_file)
                        self.existing_channels.add(data['YouTube Channel Link'])
                except Exception as e:
                    logger.error(f"A critical error occurred while processing '{username}': {e}", exc_info=True)
                    error_data = {
                        'Influencer Channel Name': f"ERROR PROCESSING: {username}",
                        'YouTube Channel Link': self.parse_username_to_url(username),
                        'Subscribers': 'N/A', 'Other Social Links': 'N/A',
                        'Description': f"Critical error during scrape: {e}",
                        'Country': 'N/A', 'Email': 'N/A', 'Niche': 'ERROR'
                    }
                    self.append_to_csv(error_data, output_file)
                finally:
                    # --- NEW: Always add the URL to check.txt after an attempt ---
                    # This ensures that even if it's skipped, filtered, or fails,
                    # we don't try to process it again on the next run.
                    if processed_url not in self.processed_urls_from_check_txt:
                        self._append_url_to_check_file(processed_url, check_file)

                time.sleep(1)
        finally:
            self.close()

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Web driver closed")
            except Exception:
                pass


def main():
    USERNAMES_FILE = "youtube_usernames.txt"
    OUTPUT_FILE = "youtube_channels_data1.csv"
    CHECK_FILE = "checks.txt"  # <<< NEW FILE

    if not os.path.exists(USERNAMES_FILE):
        sample_usernames = ["@MrBeast", "@KingdomBloggers", "@Waalaxy"]
        with open(USERNAMES_FILE, 'w', encoding='utf-8') as f:
            for username in sample_usernames: f.write(f"{username}\n")

    scraper = None
    try:
        scraper = YouTubeChannelScraper(headless=False)
        # --- MODIFIED: Pass check_file to the runner ---
        scraper.run_scraper(USERNAMES_FILE, OUTPUT_FILE, CHECK_FILE)
        logger.info("Scraping finished.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in main: {e}", exc_info=True)
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()