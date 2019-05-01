# `autopilot`: A Python library for automating Chrome

`autopilot` is a wrapper around Selenium, specifically designed to work with
Google Chrome. It implements some human-like behaviors to provide fault
tolerance and resilience when exercising production web applications, such as:

* Waiting (impatiently) for elements to load on the screen,
* Refreshing the page when things don't load as expected,
* Typing input at a human pace, and
* Reacting with a human reaction time when elements appear on screen.

## Installation

### Dependencies

Reference the [`Dockerfile`](Dockerfile) for an example of how to setup the
environment. In general, this project requires:

* WebDriver for Chromium (e.g. `apt-get install chromium-chromedriver`)
* Python 2.7 with `pip` (e.g. `apt-get install python-pip`)
* Selenium (e.g. `apt-get install python-selenium` or `pip install selenium`)

### Using `pip`

Distribution via PyPi is not yet available, but you can install the latest version directly from Github:

```bash
pip install git+https://github.com/dolph/autopilot
```

## Usage

The primary way to consume `autopilot` is to write an "autopilot module", and
then invoke the module via the `autopilot` CLI.

Here's a [minimal autopilot module](minimal_autopilot_module.py):

```python
def start(browser):
    browser.get("https://google.com/")
```

When run on the CLI, `autopilot` will launch a browser and pass the browser
session to your module's `start()` function, which will then navigate to
Google, and exit:

```bash
autopilot minimal_autopilot_module.py
```

### A real-world example

This example navigates the UPS website to obtain tracking information given a
particular tracking number.

```python
import os


def start(browser):
    # Variables are passed in via the environment. For example:
    # $ TRACKING_NUMBER="1Z..." autopilot ups_tracking.py
    tracking_number = os.environ['TRACKING_NUMBER']

    # Load the UPS website
    browser.get('https://www.ups.com/')

    # Select the English / US option
    browser.click('//a[@data-code="en_us"]')

    # Type our tracking number into the tracking text input
    browser.type('//textarea[@id="ups-track--qs"]', tracking_number)

    # Click the Tracking submit button
    browser.click('//button[@id="ups-tracking-submit"]')

    # Find the package status and scheduled delivery date
    print(browser.find('//*[@id="stApp_txtPackageStatus"]').text)
    print(browser.find('//*[@id="stApp_scheduledDelivery"]').text)
```

Note that `click()`, `type()`, and `find()` all accept
[XPaths](https://www.guru99.com/xpath-selenium.html) as their basic form of
input (which are similar to CSS selectors, but more powerful).

The output, after 10-12 seconds:

```bash
$ TRACKING_NUMBER="1Z..." autopilot ups_tracking.py
In Transit
03/27/2019
```
