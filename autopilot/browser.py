from __future__ import print_function

import os
import pickle
import random
import tempfile
import time
import uuid

from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common import action_chains
from selenium.webdriver.common import desired_capabilities as dc

from selenium.webdriver.common import keys


PROGRESS_INTERVAL = 60

HUMAN_REACTION_TIME = 0.25  # seconds
TIMEOUT = 60  # seconds
PATH_TO_CHROMEDRIVER = os.environ.get(
    'CHROMEDRIVER', '/usr/lib/chromium-browser/chromedriver')
USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/69.0.3497.100 Safari/537.36')
COOKIES_FILE = os.path.expanduser('~/.autopilot/cookies.pkl')

# Wrap external objects so that we can access them from elsewhere within this
# package.
TimeoutException = exceptions.TimeoutException
NoSuchElementException = exceptions.NoSuchElementException
Keys = keys.Keys


class NotFound(Exception):
    def __init__(self, xpath, timeout):
        super(NotFound, self).__init__(
            '%d second timeout exceeded trying to find %s' % (
                timeout, xpath))


def lag(x=None):
    """Add a reasonable human reaction time before returning the input."""
    try:
        return x
    finally:
        time.sleep(HUMAN_REACTION_TIME)


def random_lag(x=None):
    """Add a reasonable human reaction time before returning the input."""
    try:
        return x
    finally:
        time.sleep(
            random.uniform(HUMAN_REACTION_TIME / 5, HUMAN_REACTION_TIME / 2))
        pass


def long_lag(x=None):
    """Add a reasonable human reaction time before returning the input."""
    time.sleep(
        random.uniform(HUMAN_REACTION_TIME / 2, HUMAN_REACTION_TIME * 5))
    return x


class Browser(object):
    def __init__(self, headless=False, fullscreen=False):
        """Initialize a remotely controlled browser.

        If headless mode, the browser will not expect to be rendered onto a
        screen. This is handy for running in a Docker container, or in CI, for
        example.

        In fullscreen mode, the browser stretches itself to full screen on
        startup.

        """
        if headless and fullscreen:
            raise Exception(
                'Headless and fullscreen modes are not compatible.')

        self.service = service.Service(PATH_TO_CHROMEDRIVER)
        self.service.start()

        # This is the desired resolution for screenshots. The actual window
        # size will be calculated with an offset for menus, etc.

        resolution = os.environ.get('BROWSER_RESOLUTION', '1280x800')
        resolution = resolution.split('x')
        resolution = (int(resolution[0]), int(resolution[1]))

        capabilities = dc.DesiredCapabilities.CHROME
        capabilities['chrome.binary'] = '/opt/google/chrome/google-chrome'
        capabilities['loggingPrefs'] = {'browser': 'ALL'}
        capabilities['chromeOptions'] = {'args': [
            '--user-agent="%s"' % USER_AGENT,
            '--window-size=%d,%d' % (
                resolution[0],
                resolution[1] + 72),
            '--disable-infobars',  # Hide "Chrome is being controlled..."
        ]}

        if headless:
            capabilities['chromeOptions']['useAutomationExtension'] = False
            capabilities['chromeOptions']['args'].extend([
                '--headless',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ])

        self.driver = webdriver.Remote(self.service.service_url, capabilities)
        self.driver.set_page_load_timeout(TIMEOUT)
        self.driver.set_script_timeout(TIMEOUT)

        if fullscreen:
            self.driver.fullscreen_window()

    @property
    def cookies(self):
        return self.driver.get_cookies()

    def save_cookies(self):
        try:
            os.mkdir(os.path.dirname(COOKIES_FILE))
        except OSError:
            pass

        with open(COOKIES_FILE, 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)

    def load_cookies(self):
        if not os.path.isfile(COOKIES_FILE):
            return

        with open(COOKIES_FILE, 'rb') as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

    @property
    def logs(self):
        return self.driver.get_log('browser')

    @property
    def url(self):
        return self.driver.current_url

    def quit(self):
        print('QUIT')
        self.driver.quit()

    def refresh(self, log=True):
        if log:
            print('REFRESH')
        self.driver.refresh()

    def switch_tab(self, index):
        print('SWITCH tab %s' % index)
        lag(self.driver.switch_to.window(self.driver.window_handles[index]))

    def close_tab(self):
        print('CLOSE current tab')
        self.driver.close()

    def get(self, url):
        print('GET %s' % url)
        try:
            lag(self.driver.get(url))
        except TimeoutException:
            lag(self.driver.get(url))

    def finds(self, xpath, visible=True, enabled=True):
        """Returns zero to many matching DOM elements.

        Unlike `find()`, this method will return successfully even if there are
        no matches.

        """
        elements = self.driver.find_elements_by_xpath(xpath)

        filtered = []
        for element in elements:
            try:
                if visible and not element.is_displayed():
                    continue

                if enabled and not element.is_enabled():
                    continue
            except exceptions.StaleElementReferenceException:
                continue

            # This element is displayed and enabled
            filtered.append(element)
        elements = filtered

        return lag(elements)

    def find(self, xpath, visible=True, enabled=True,
             refresh=None, timeout=TIMEOUT):
        print('FIND %s (timeout=%ds)' % (xpath, timeout))

        started_at = time.time()
        refreshed_at = time.time()
        progressed_at = time.time()

        # Find the element
        while True:
            if time.time() - started_at > timeout:
                raise NotFound(xpath, timeout)

            if time.time() - progressed_at > PROGRESS_INTERVAL:
                progressed_at = time.time()
                print('.', end='')

            if refresh and time.time() - refreshed_at > refresh:
                self.refresh(log=refresh >= 15)
                refreshed_at = time.time()

            elements = self.finds(
                xpath,
                visible=visible,
                enabled=enabled)

            if elements:
                if len(elements) > 1:
                    print('WARNING: Ignoring %d additional matching elements.'
                          % (len(elements) - 1))

                # Do not add lag here, because finds() already did.
                return elements[0]

            time.sleep(0.1)

    def present(self, xpath, refresh=None,
                timeout=TIMEOUT):
        """Returns true when an element can be found."""
        print('PRESENT %s (timeout=%ds)' % (xpath, timeout))

        started_at = time.time()
        refreshed_at = time.time()
        progressed_at = time.time()

        # Find the element, or lack thereof
        while True:
            if timeout and time.time() - started_at > timeout:
                return False

            if refresh and time.time() - refreshed_at > refresh:
                self.refresh(log=refresh >= 15)
                refreshed_at = time.time()

            if time.time() - progressed_at > PROGRESS_INTERVAL:
                progressed_at = time.time()
                print('.', end='')

            elements = self.finds(
                xpath,
                visible=None,
                enabled=None)

            if elements:
                # Do not add lag here, because finds() already did.
                return True

            time.sleep(0.1)

    def absent(self, xpath, refresh=None, timeout=TIMEOUT):
        """Returns true when an element cannot be found."""
        print('ABSENT %s (timeout=%ds)' % (xpath, timeout))

        started_at = time.time()
        refreshed_at = time.time()
        progressed_at = time.time()

        # Find the element, or lack thereof
        while True:
            if time.time() - started_at > timeout:
                return False

            if time.time() - progressed_at > PROGRESS_INTERVAL:
                progressed_at = time.time()
                print('.', end='')

            if refresh and time.time() - refreshed_at > refresh:
                self.refresh(log=refresh >= 15)
                refreshed_at = time.time()

            elements = self.finds(
                xpath,
                visible=None,
                enabled=None)

            if not elements:
                # Do not add lag here, because finds() already did.
                return True

    def hover(self, xpath, refresh=None, timeout=TIMEOUT, click=False):
        """Scrolls to the element and hovers the mouse cursor over it."""
        if not click:
            print('HOVER %s (timeout=%ds)' % (xpath, timeout))
        started_at = time.time()
        progressed_at = time.time()

        # Click the element.
        while True:
            if time.time() - started_at > timeout:
                raise NotFound(xpath, timeout)

            if time.time() - progressed_at > PROGRESS_INTERVAL:
                progressed_at = time.time()
                print('.', end='')

            try:
                element = self.find(
                    xpath,
                    refresh=refresh,
                    timeout=timeout - (time.time() - started_at))

                action_chains.ActionChains(self.driver)\
                    .move_to_element(element)\
                    .perform()

                if click:
                    return long_lag(element).click()
                else:
                    return long_lag(element)
            except (exceptions.WebDriverException,
                    exceptions.StaleElementReferenceException):
                pass

            time.sleep(0.1)

    def click(self, xpath, refresh=None, timeout=TIMEOUT):
        """Simulate the mouse cursor finding and clicking a DOM element."""
        print('CLICK %s (timeout=%ds)' % (xpath, timeout))
        return self.hover(xpath, refresh=refresh, timeout=timeout, click=True)

    def type(self, xpath, value, enter=False, refresh=None,
             timeout=TIMEOUT):
        element = self.find(xpath, refresh=refresh, timeout=timeout)

        print("TYPE %s (timeout=%ds)" % (
            element.get_attribute('outerHTML'), timeout))

        # Type into the element.
        for key in value:
            random_lag(element.send_keys(key))
        if enter:
            time.sleep(HUMAN_REACTION_TIME)
            random_lag(element.send_keys(Keys.ENTER))
        return element

    def goto(self, url):
        """Go to a URL in the first tab, if we're not already there."""
        if not self.url.startswith(url):
            self.get(url)

    def screenshot(self):
        filename = '%d-%s.png' % (time.time(), uuid.uuid4().hex)
        path = os.path.join(tempfile.gettempdir(), filename)
        try:
            self.driver.get_screenshot_as_file(path)
        except TimeoutException:
            # Retry once, but the browser might just be gone
            self.driver.get_screenshot_as_file(path)
        print('SCREENSHOT %s' % path)
        return path
