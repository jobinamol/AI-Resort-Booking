import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from projectapp.models import Package, Resort, GuestUser, Booking
from datetime import datetime, timedelta
import time
import json

class BookingTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome options for testing
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Create test user and resort
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testresort',
            email='resort@test.com',
            password='testpass123'
        )
        
        self.resort = Resort.objects.create(
            resort_name='Test Resort',
            location='Test Location',
            owner=self.user
        )

        # Create test packages
        self.daycation_package = Package.objects.create(
            package_name='Test Daycation',
            description='Test Daycation Description',
            price=1000,
            package_type='daycation',
            resort=self.resort,
            max_guests=4
        )

        self.staycation_package = Package.objects.create(
            package_name='Test Staycation',
            description='Test Staycation Description',
            price=2000,
            package_type='staycation',
            resort=self.resort,
            max_guests=4
        )

        # Create test guest user
        self.guest_user = GuestUser.objects.create(
            full_name='Test Guest',
            email='guest@test.com',
            mobile_number='1234567890'
        )

    def test_daycation_booking_flow(self):
        """Test the complete daycation booking process"""
        # Navigate to package detail page
        self.selenium.get(f'{self.live_server_url}{reverse("package_detail", args=[self.daycation_package.id])}')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'booking-form'))
        )

        # Fill booking form
        self.selenium.find_element(By.NAME, 'full_name').send_keys('Test Guest')
        self.selenium.find_element(By.NAME, 'email').send_keys('guest@test.com')
        self.selenium.find_element(By.NAME, 'phone').send_keys('1234567890')
        
        # Set date (tomorrow)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        date_input = self.selenium.find_element(By.NAME, 'check_in')
        self.selenium.execute_script(f"arguments[0].value = '{tomorrow}'", date_input)
        
        # Set number of guests
        self.selenium.find_element(By.NAME, 'guests').send_keys('2')
        
        # Add special requests
        self.selenium.find_element(By.NAME, 'special_requests').send_keys('Test special request')
        
        # Submit booking form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for payment form
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'razorpay-payment-button'))
        )
        
        # Verify booking data in session
        session_data = self.client.session.get('booking_data')
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data['package_id'], self.daycation_package.id)

    def test_staycation_booking_flow(self):
        """Test the complete staycation booking process"""
        # Navigate to package detail page
        self.selenium.get(f'{self.live_server_url}{reverse("package_detail", args=[self.staycation_package.id])}')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'booking-form'))
        )

        # Fill booking form
        self.selenium.find_element(By.NAME, 'full_name').send_keys('Test Guest')
        self.selenium.find_element(By.NAME, 'email').send_keys('guest@test.com')
        self.selenium.find_element(By.NAME, 'phone').send_keys('1234567890')
        
        # Set check-in date (tomorrow)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        checkin_input = self.selenium.find_element(By.NAME, 'check_in')
        self.selenium.execute_script(f"arguments[0].value = '{tomorrow}'", checkin_input)
        
        # Set check-out date (day after tomorrow)
        day_after = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        checkout_input = self.selenium.find_element(By.NAME, 'check_out')
        self.selenium.execute_script(f"arguments[0].value = '{day_after}'", checkout_input)
        
        # Set number of guests
        self.selenium.find_element(By.NAME, 'guests').send_keys('2')
        
        # Submit booking form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for payment form
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'razorpay-payment-button'))
        )

    def test_booking_validation(self):
        """Test booking form validation"""
        # Navigate to package detail page
        self.selenium.get(f'{self.live_server_url}{reverse("package_detail", args=[self.daycation_package.id])}')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'booking-form'))
        )

        # Submit empty form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for error messages
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'invalid-feedback'))
        )
        
        # Verify error messages
        error_messages = self.selenium.find_elements(By.CLASS_NAME, 'invalid-feedback')
        self.assertGreater(len(error_messages), 0)

    def test_guest_login_booking(self):
        """Test booking process with guest login"""
        # Log in as guest
        self.client.login(email='guest@test.com', password='guestpass123')
        cookie = self.client.cookies['sessionid']
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie({
            'name': 'sessionid',
            'value': cookie.value,
            'secure': False,
            'path': '/'
        })

        # Navigate to package detail page
        self.selenium.get(f'{self.live_server_url}{reverse("package_detail", args=[self.daycation_package.id])}')
        
        # Wait for page to load and verify pre-filled data
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'booking-form'))
        )
        
        name_field = self.selenium.find_element(By.NAME, 'full_name')
        self.assertEqual(name_field.get_attribute('value'), self.guest_user.full_name)

    def test_booking_confirmation(self):
        """Test booking confirmation page"""
        # Create a test booking
        booking = Booking.objects.create(
            guest=self.guest_user,
            package=self.daycation_package,
            resort=self.resort,
            check_in=datetime.now().date(),
            check_out=datetime.now().date(),
            adults=2,
            total_amount=2000,
            booking_status='confirmed',
            payment_status='paid'
        )
        
        # Navigate to booking confirmation page
        self.selenium.get(f'{self.live_server_url}{reverse("booking_confirmation", args=[booking.id])}')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'booking-details'))
        )
        
        # Verify booking details are displayed
        booking_details = self.selenium.find_element(By.CLASS_NAME, 'booking-details').text
        self.assertIn(self.daycation_package.package_name, booking_details)
        self.assertIn(self.guest_user.full_name, booking_details)

    def test_past_date_validation(self):
        """Test validation for past dates"""
        # Navigate to package detail page
        self.selenium.get(f'{self.live_server_url}{reverse("package_detail", args=[self.daycation_package.id])}')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'booking-form'))
        )

        # Try to set past date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        date_input = self.selenium.find_element(By.NAME, 'check_in')
        self.selenium.execute_script(f"arguments[0].value = '{yesterday}'", date_input)
        
        # Fill other required fields
        self.selenium.find_element(By.NAME, 'full_name').send_keys('Test Guest')
        self.selenium.find_element(By.NAME, 'email').send_keys('guest@test.com')
        self.selenium.find_element(By.NAME, 'phone').send_keys('1234567890')
        self.selenium.find_element(By.NAME, 'guests').send_keys('2')
        
        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for error message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-danger'))
        )
        
        # Verify error message
        error_message = self.selenium.find_element(By.CLASS_NAME, 'alert-danger').text
        self.assertIn('past date', error_message.lower())

    def test_guest_count_validation(self):
        """Test validation for guest count limits"""
        # Navigate to package detail page
        self.selenium.get(f'{self.live_server_url}{reverse("package_detail", args=[self.daycation_package.id])}')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'booking-form'))
        )

        # Fill form with invalid guest count
        self.selenium.find_element(By.NAME, 'full_name').send_keys('Test Guest')
        self.selenium.find_element(By.NAME, 'email').send_keys('guest@test.com')
        self.selenium.find_element(By.NAME, 'phone').send_keys('1234567890')
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        date_input = self.selenium.find_element(By.NAME, 'check_in')
        self.selenium.execute_script(f"arguments[0].value = '{tomorrow}'", date_input)
        
        # Set invalid number of guests (more than max_guests)
        self.selenium.find_element(By.NAME, 'guests').send_keys('10')
        
        # Submit form
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for error message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-danger'))
        )
        
        # Verify error message
        error_message = self.selenium.find_element(By.CLASS_NAME, 'alert-danger').text
        self.assertIn('guest', error_message.lower()) 