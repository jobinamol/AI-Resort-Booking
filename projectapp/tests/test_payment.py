import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test import Client
from projectapp.models import Package, Resort, GuestUser, Booking, BookingPayment
from datetime import datetime
import json
import time

class PaymentTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        # Create test data
        self.guest_user = GuestUser.objects.create(
            full_name='Test Guest',
            email='guest@test.com',
            mobile_number='1234567890'
        )
        
        self.resort = Resort.objects.create(
            resort_name='Test Resort',
            location='Test Location'
        )
        
        self.package = Package.objects.create(
            package_name='Test Package',
            description='Test Description',
            price=1000,
            package_type='daycation',
            resort=self.resort
        )

    def test_payment_initialization(self):
        """Test payment initialization process"""
        # Create booking session data
        session = self.client.session
        session['booking_data'] = {
            'package_id': self.package.id,
            'guest_id': self.guest_user.id,
            'check_in': datetime.now().strftime('%Y-%m-%d'),
            'guests': 2,
            'amount': 2000,
            'email': 'guest@test.com',
            'phone': '1234567890'
        }
        session.save()

        # Add session cookie to selenium
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie({
            'name': 'sessionid',
            'value': self.client.cookies['sessionid'].value,
            'secure': False,
            'path': '/'
        })

        # Navigate to payment page
        self.selenium.get(f'{self.live_server_url}{reverse("package_booking", args=[self.package.id])}')
        
        # Wait for Razorpay button
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'razorpay-payment-button'))
        )
        
        # Verify payment amount
        payment_button = self.selenium.find_element(By.ID, 'razorpay-payment-button')
        self.assertIn('2000', payment_button.get_attribute('data-amount'))

    def test_payment_verification(self):
        """Test payment verification process"""
        # Create test booking data
        booking_data = {
            'razorpay_payment_id': 'test_payment_id',
            'razorpay_order_id': 'test_order_id',
            'razorpay_signature': 'test_signature'
        }

        # Create session data
        session = self.client.session
        session['booking_data'] = {
            'package_id': self.package.id,
            'guest_id': self.guest_user.id,
            'check_in': datetime.now().strftime('%Y-%m-%d'),
            'guests': 2,
            'amount': 2000
        }
        session.save()

        # Add session cookie to selenium
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie({
            'name': 'sessionid',
            'value': self.client.cookies['sessionid'].value,
            'secure': False,
            'path': '/'
        })

        # Simulate payment verification request
        response = self.client.post(reverse('verify_payment'), booking_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify booking was created
        self.assertTrue(Booking.objects.filter(guest=self.guest_user, package=self.package).exists())

    def test_payment_error_handling(self):
        """Test payment error handling"""
        # Create invalid payment data
        invalid_data = {
            'razorpay_payment_id': 'invalid_id',
            'razorpay_order_id': 'invalid_order',
            'razorpay_signature': 'invalid_signature'
        }

        # Create session data
        session = self.client.session
        session['booking_data'] = {
            'package_id': self.package.id,
            'guest_id': self.guest_user.id,
            'check_in': datetime.now().strftime('%Y-%m-%d'),
            'guests': 2,
            'amount': 2000
        }
        session.save()

        # Add session cookie to selenium
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie({
            'name': 'sessionid',
            'value': self.client.cookies['sessionid'].value,
            'secure': False,
            'path': '/'
        })

        # Simulate invalid payment verification
        response = self.client.post(reverse('verify_payment'), invalid_data)
        self.assertEqual(response.status_code, 400)

    def test_payment_confirmation(self):
        """Test payment confirmation page"""
        # Create a confirmed booking with payment
        booking = Booking.objects.create(
            guest=self.guest_user,
            package=self.package,
            resort=self.resort,
            check_in=datetime.now().date(),
            check_out=datetime.now().date(),
            adults=2,
            total_amount=2000,
            booking_status='confirmed',
            payment_status='paid',
            razorpay_order_id='test_order_id'
        )

        payment = BookingPayment.objects.create(
            booking=booking,
            amount=2000,
            payment_method='razorpay',
            transaction_id='test_payment_id',
            razorpay_order_id='test_order_id',
            payment_status='success'
        )

        # Navigate to booking confirmation page
        self.selenium.get(f'{self.live_server_url}{reverse("booking_confirmation", args=[booking.id])}')
        
        # Wait for confirmation details
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'booking-details'))
        )
        
        # Verify confirmation details
        confirmation_text = self.selenium.find_element(By.CLASS_NAME, 'booking-details').text
        self.assertIn(self.package.package_name, confirmation_text)
        self.assertIn('paid', confirmation_text.lower())
        self.assertIn('test_payment_id', confirmation_text)

    def test_session_cleanup(self):
        """Test session cleanup after payment"""
        # Create session data
        session = self.client.session
        session['booking_data'] = {
            'package_id': self.package.id,
            'guest_id': self.guest_user.id,
            'check_in': datetime.now().strftime('%Y-%m-%d'),
            'guests': 2,
            'amount': 2000
        }
        session.save()

        # Simulate successful payment
        payment_data = {
            'razorpay_payment_id': 'test_payment_id',
            'razorpay_order_id': 'test_order_id',
            'razorpay_signature': 'test_signature'
        }

        # Add session cookie to selenium
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie({
            'name': 'sessionid',
            'value': self.client.cookies['sessionid'].value,
            'secure': False,
            'path': '/'
        })

        # Make payment verification request
        response = self.client.post(reverse('verify_payment'), payment_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify session data was cleaned
        session = self.client.session
        self.assertNotIn('booking_data', session) 