"""
WeChat Web Automation Module
Uses Selenium to control web.wechat.com
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeChatWebAutomation:
    def __init__(self):
        self.driver = None
        self.logged_in = False

    def start_browser(self):
        """Start Chrome browser with WeChat Web"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            # Keep browser open
            chrome_options.add_experimental_option("detach", True)

            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Navigate to WeChat Web
            self.driver.get('https://web.wechat.com/')
            logger.info("Browser started, navigating to WeChat Web")

            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    def wait_for_login(self, timeout=60):
        """Wait for user to scan QR code and log in"""
        try:
            logger.info("Waiting for QR code scan...")

            # Wait for the main chat interface to appear
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat_list"))
            )

            self.logged_in = True
            logger.info("✓ Successfully logged in to WeChat Web")
            return True

        except TimeoutException:
            logger.error("Login timeout - QR code not scanned")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def find_chat(self, chat_name):
        """Find and open a specific chat"""
        try:
            if not self.logged_in:
                logger.error("Not logged in")
                return False

            # Click on search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search_bar"))
            )
            search_box.click()
            time.sleep(0.5)

            # Type chat name
            search_input = self.driver.find_element(By.CSS_SELECTOR, "input.frm_search")
            search_input.clear()
            search_input.send_keys(chat_name)
            time.sleep(1)

            # Click on first result
            first_result = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search_item"))
            )
            first_result.click()
            time.sleep(1)

            logger.info(f"✓ Opened chat: {chat_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to find chat '{chat_name}': {e}")
            return False

    def send_message(self, message):
        """Send a message in the current chat"""
        try:
            if not self.logged_in:
                logger.error("Not logged in")
                return False

            # Find message input area
            input_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "editArea"))
            )

            # Type message
            input_area.clear()
            input_area.send_keys(message)
            time.sleep(0.5)

            # Click send button
            send_button = self.driver.find_element(By.CSS_SELECTOR, "a.btn.btn_send")
            send_button.click()

            logger.info(f"✓ Message sent: {message[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def get_unread_messages(self):
        """Get list of unread messages"""
        try:
            if not self.logged_in:
                return []

            unread_chats = []

            # Find all chat items with unread badge
            chat_items = self.driver.find_elements(By.CSS_SELECTOR, ".chat_item.on")

            for chat in chat_items:
                try:
                    # Check if has unread badge
                    badge = chat.find_element(By.CSS_SELECTOR, ".web_wechat_reddot_middle")
                    if badge:
                        chat_name = chat.find_element(By.CSS_SELECTOR, ".nickname").text
                        unread_chats.append(chat_name)
                except NoSuchElementException:
                    continue

            return unread_chats

        except Exception as e:
            logger.error(f"Failed to get unread messages: {e}")
            return []

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


# Global instance
wechat_web = WeChatWebAutomation()
