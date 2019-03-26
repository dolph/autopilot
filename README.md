# `autopilot`: A Python wrapper for Selenium.

`autopilot` is a wrapper around Selenium, specifically designed to work with
Google Chrome, which implements some common human-behaviors so that your
implementation doesn't have to. For example,

* Waiting (impatiently) for elements to load on the screen
* Refreshing the page when things don't load as expected

## Installing dependencies

Reference the [`Dockerfile`](Dockerfile) for an example of how to setup the
environment. In general, this project requires:

* WebDriver for Chromium
* Python 2.7 with `pip`
* Selenium
