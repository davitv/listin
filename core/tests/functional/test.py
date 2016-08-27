from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
import os
import time
from profiles.models import User
from business.models import Organization

REGISTER_EMAIL = 'davitvl@mail.ru'
REGISTER_PASS = '@120804a'
TEST_PHONE = '+37494303029'
TEST_FIRST_NAME = 'John'
TEST_LAST_NAME = 'Johnson'

BUSINESS_NAME = "Some Title"
BUSINESS_EMAIL = "business@listin.ru"
BUSINESS_PHONE = "+79261473805"
BUSINESS_URL = "http://listin.ru"
BUSINESS_INN = "79261473805"
BUSINESS_OGRN = "123456789"
BUSINESS_COUNTRY = "IT"
BUSINESS_STATE = "Alabama"
BUSINESS_ADDRESS_1 = "Broadway str. 7"
BUSINESS_ADDRESS_2 = "Lowrider Ave."


class WebsiteTester(StaticLiveServerTestCase):
    def setUp(self):
        chromedriver = "/usr/share/chrome/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        self.driver = webdriver.Chrome(chromedriver)

    def tearDown(self):
        self.driver.close()

    def log_user_in(self, email, password):
        self.driver.get(self.live_server_url + reverse('login'))
        login_form = self.driver.find_element_by_id("login-form")
        input_email = login_form.find_element_by_name("username")
        input_pass = login_form.find_element_by_name("password")
        input_email.send_keys(email)
        input_pass.send_keys(password)
        self.driver.find_element_by_id("login-submit").click()

    def signup_new_user(self, email, password):
        self.driver.get(self.live_server_url + reverse('signup'))
        signup_form = self.driver.find_element_by_id("signup-form")
        input_email = signup_form.find_element_by_name("email")
        input_password1 = signup_form.find_element_by_name("password1")
        input_password2 = signup_form.find_element_by_name("password2")

        input_email.send_keys(email)
        input_password1.send_keys(password)
        input_password2.send_keys(password)

        submit_btn = signup_form.find_element_by_tag_name("button")
        submit_btn.click()

    def create_test_user(self, email=None, password=None):
        user = User(email=email or REGISTER_EMAIL)
        user.set_password(REGISTER_PASS or REGISTER_PASS)
        user.save()
        return user


class TestListin(WebsiteTester):
    def test_correct_signup_data(self):
        self.signup_new_user(REGISTER_EMAIL, REGISTER_PASS)
        self.assertTrue("Confirmation email was sent." in self.driver.page_source)
        self.assertTrue("Welcome!" in self.driver.page_source)

    def test_incorrect_signup_data(self):
        self.signup_new_user(REGISTER_EMAIL, "123")
        self.assertTrue("This password is too short. It must contain at least 8 characters." in self.driver.page_source)

    def test_correct_login_data(self):
        self.create_test_user()
        self.log_user_in(REGISTER_EMAIL, REGISTER_PASS)
        self.assertTrue("Profile Information" in self.driver.page_source)

    def test_incorrect_login_data(self):
        self.create_test_user()
        self.log_user_in(REGISTER_EMAIL + "s", REGISTER_PASS + "s")
        self.assertTrue("Please enter a correct email address and password" in self.driver.page_source)

    def test_personal_info_form(self):
        self.create_test_user()
        self.log_user_in(REGISTER_EMAIL, REGISTER_PASS)
        profile_form = self.driver.find_element_by_id("profile-form")
        first_name = profile_form.find_element_by_name("first_name")
        last_name = profile_form.find_element_by_name("last_name")
        phone_number = profile_form.find_element_by_name("phone")
        submit_btn = profile_form.find_element_by_tag_name("button")

        first_name.send_keys(TEST_FIRST_NAME)
        last_name.send_keys(TEST_LAST_NAME)
        phone_number.send_keys(TEST_PHONE)
        submit_btn.click()

        # wait until ajax response, selenium webdriver
        # waits aren't working here, don't know why
        time.sleep(1)
        self.assertTrue("Profile info saved" in self.driver.page_source)
        u = User.objects.get(email=REGISTER_EMAIL)
        self.assertEqual(u.first_name, TEST_FIRST_NAME)
        self.assertEqual(u.last_name, TEST_LAST_NAME)
        self.assertEqual(u.email, REGISTER_EMAIL)
        self.assertEqual(u.phone, TEST_PHONE)

    def test_business_info_form(self):
        self.create_test_user()
        self.log_user_in(REGISTER_EMAIL, REGISTER_PASS)

        organization_form_tab = self.driver.find_element_by_link_text('Business')
        organization_form_tab.click()

        company_form = self.driver.find_element_by_id("organization-form")

        name = company_form.find_element_by_name("name")
        url = company_form.find_element_by_name("url")
        email = company_form.find_element_by_name("email")
        phone = company_form.find_element_by_name("phone")
        inn = company_form.find_element_by_name("inn")
        ogrn = company_form.find_element_by_name("ogrn")
        country = company_form.find_element_by_name("country")
        state = company_form.find_element_by_name("state")
        address_1 = company_form.find_element_by_name("address_1")
        address_2 = company_form.find_element_by_name("address_2")
        description = company_form.find_element_by_name("description")

        submit_btn = company_form.find_element_by_tag_name("button")

        name.send_keys(BUSINESS_NAME)
        url.send_keys(BUSINESS_URL)
        email.send_keys(BUSINESS_EMAIL)
        phone.send_keys(BUSINESS_PHONE)
        address_1.send_keys(BUSINESS_ADDRESS_1)
        address_2.send_keys(BUSINESS_ADDRESS_2)
        ogrn.send_keys(BUSINESS_OGRN)
        inn.send_keys(BUSINESS_INN)
        state.send_keys(BUSINESS_STATE)
        country.send_keys(BUSINESS_COUNTRY)
        description.send_keys("ABCDEF")
        submit_btn.click()

        # wait until ajax response, selenium webdriver
        # waits aren't working here, don't know why
        time.sleep(1)
        self.assertTrue("Business data saved" in self.driver.page_source)
        b = Organization.objects.get(user__email=REGISTER_EMAIL, branch__isnull=True)
        self.assertEqual(b.name, BUSINESS_NAME)
        self.assertEqual(b.url, BUSINESS_URL)
        self.assertEqual(b.email, BUSINESS_EMAIL)
        self.assertEqual(b.phone, BUSINESS_PHONE)
        self.assertEqual(b.address_1, BUSINESS_ADDRESS_1)
        self.assertEqual(b.address_2, BUSINESS_ADDRESS_2)
        self.assertEqual(b.ogrn, BUSINESS_OGRN)
        self.assertEqual(b.inn, BUSINESS_INN)
        self.assertEqual(b.state, BUSINESS_STATE)
        self.assertEqual(b.state, BUSINESS_STATE)
        self.assertEqual(b.country, BUSINESS_COUNTRY)




