# `testpilot`: browser-based test driver for IBM Cloud

[![Build Status](https://travis.ibm.com/Dolph-Mathews/browser-testing.svg?token=CGaMNLqqASCMosep55aJ&branch=master)](https://travis.ibm.com/Dolph-Mathews/browser-testing)

**WARNING**: This will delete EVERYTHING in your IBM Cloud account.

`testpilot` is a wrapper around Selenium, specifically designed to work with
Google Chrome, which implements some common human-behaviors so that you're test
implementation doesn't have. For example,

* Waiting (impatiently) for elements to load on the screen
* Refreshing the page when things don't load as expected

## Installing dependencies

Reference the `Dockerfile` for an example of how to setup the environment. In
general, this project requires:

* WebDriver for Chromium
* Python 2.7 with `pip`
* Selenium
