from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import unittest

class TestLogin(unittest.TestCase):
    def setUp(self):
        # Setup Chrome WebDriver with Service and Options
        service = Service(ChromeDriverManager().install())
        self.options = Options()
        # Add options for better testing
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-notifications")
        # self.options.add_argument("--headless")  # Uncomment for headless testing
        
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.base_url = "http://localhost:8000"
        self.login_url = f"{self.base_url}/accounts/login/"
        
    def test_successful_login(self):
        """Test successful login with valid credentials"""
        driver = self.driver
        
        # Navigate to the login page
        driver.get(self.login_url)
        
        try:
            # Wait for username field and enter username
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys("Jobinamol")
            
            # Find password field and enter password
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys("Jobina@123*")
            
            # Find and click the remember me checkbox
            remember_me = driver.find_element(By.NAME, "remember_me")
            if not remember_me.is_selected():
                remember_me.click()
            
            # Find and click the submit button
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for successful login and verify
            WebDriverWait(driver, 10).until(
                EC.url_changes(self.login_url)
            )
            
            # Verify successful login
            self.assertNotEqual(driver.current_url, self.login_url)
            
        except Exception as e:
            print(f"An error occurred in test_successful_login: {str(e)}")
            driver.save_screenshot("login_success_error.png")
            raise

    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        driver = self.driver
        
        driver.get(self.login_url)
        
        try:
            # Enter invalid credentials
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys("invalid_user")
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys("invalid_password")
            
            # Submit form
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for error message - try multiple possible selectors
            try:
                error_message = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
                )
            except TimeoutException:
                try:
                    error_message = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "alert"))
                    )
                except TimeoutException:
                    error_message = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='alert']"))
                    )
            
            # Verify we're still on login page and error is shown
            self.assertEqual(driver.current_url, self.login_url)
            self.assertTrue(error_message.is_displayed())
            self.assertTrue("Invalid username or password" in driver.page_source)
            
        except Exception as e:
            print(f"An error occurred in test_invalid_credentials: {str(e)}")
            driver.save_screenshot("login_invalid_error.png")
            raise

    def test_empty_fields(self):
        """Test login with empty fields"""
        driver = self.driver
        
        driver.get(self.login_url)
        
        try:
            # Find and click submit without entering any credentials
            submit_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            )
            submit_button.click()
            
            # Verify form validation (HTML5 validation should prevent submission)
            username_field = driver.find_element(By.NAME, "username")
            self.assertTrue(username_field.get_attribute("required"))
            
            # Verify we're still on login page
            self.assertEqual(driver.current_url, self.login_url)
            
        except Exception as e:
            print(f"An error occurred in test_empty_fields: {str(e)}")
            driver.save_screenshot("login_empty_error.png")
            raise

    def test_forgot_password_link(self):
        """Test forgot password link"""
        driver = self.driver
        
        driver.get(self.login_url)
        
        try:
            # Try multiple possible selectors for the forgot password link
            try:
                forgot_password_link = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.forgot-password"))
                )
            except TimeoutException:
                try:
                    forgot_password_link = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "Forgot Password?"))
                    )
                except TimeoutException:
                    forgot_password_link = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Forgot"))
                    )
            
            # Get the href attribute before clicking
            forgot_password_url = forgot_password_link.get_attribute("href")
            forgot_password_link.click()
            
            # Wait for URL change and verify
            WebDriverWait(driver, 10).until(
                lambda driver: driver.current_url == forgot_password_url
            )
            
            self.assertTrue("forgot_password" in driver.current_url.lower())
            
        except Exception as e:
            print(f"An error occurred in test_forgot_password_link: {str(e)}")
            driver.save_screenshot("forgot_password_error.png")
            raise

    def test_create_account_link(self):
        """Test create account link"""
        driver = self.driver
        
        driver.get(self.login_url)
        
        try:
            # Find and click create account link
            create_account_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Create Account"))
            )
            create_account_link.click()
            
            # Verify redirect to signup page
            WebDriverWait(driver, 10).until(
                EC.url_contains("signup")
            )
            
        except Exception as e:
            print(f"An error occurred in test_create_account_link: {str(e)}")
            driver.save_screenshot("create_account_error.png")
            raise

    def test_remember_me_functionality(self):
        """Test remember me checkbox functionality"""
        driver = self.driver
        
        driver.get(self.login_url)
        
        try:
            # Find and verify remember me checkbox
            remember_me = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "remember_me"))
            )
            
            # Verify checkbox is initially unchecked
            self.assertFalse(remember_me.is_selected())
            
            # Click checkbox and verify it's checked
            remember_me.click()
            self.assertTrue(remember_me.is_selected())
            
            # Click again and verify it's unchecked
            remember_me.click()
            self.assertFalse(remember_me.is_selected())
            
        except Exception as e:
            print(f"An error occurred in test_remember_me_functionality: {str(e)}")
            driver.save_screenshot("remember_me_error.png")
            raise

    def tearDown(self):
        # Close the browser
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    unittest.main() 