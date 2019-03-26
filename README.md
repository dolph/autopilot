# `autopilot`: A Python wrapper for Selenium.

`autopilot` is a wrapper around Selenium, specifically designed to work with
Google Chrome, which implements some common human-behaviors so that your
implementation doesn't have to. For example,

* Waiting (impatiently) for elements to load on the screen,
* Refreshing the page when things don't load as expected,
* Typing input at a human pace, and
* Reacting with a human reaction time when elements appear on screen.

These behaviors provide fault tolerance and resilience when, for example,
testing real web applications.

## Installation

### Dependencies

Reference the [`Dockerfile`](Dockerfile) for an example of how to setup the
environment. In general, this project requires:

* WebDriver for Chromium (e.g. `apt-get install chromium-chromedriver`)
* Python 2.7 with `pip` (e.g. `apt-get install python-pip`)
* Selenium (e.g. `pip install selenium`)

### Using `pip`

Distribution via PyPi is not yet available.

```bash
pip install .
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
