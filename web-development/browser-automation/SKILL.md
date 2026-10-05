---
name: browser-automation
description: "Browser automation: Selenium 4 patterns, Playwright pick."
version: 1.0.0
author: Hermes Agent (from SeleniumHQ/selenium; offline checks run live)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [selenium, playwright, browser-automation, testing, webdriver, scraping, e2e]
    related_skills: [windows-desktop-e2e, scrapling, dogfood, har-derived-api-client, react-ecosystem]
---

<!-- source: SeleniumHQ/selenium (Apache-2.0) + selenium 4.50.0 pip-installed; no browser session was started (the first run would download a chromedriver), so driver behaviour below is documentation-sourced and labelled -->

# Browser automation (Selenium first, Playwright as the alternative)

## What This Skill Does

Chooses between Selenium and Playwright for a web task and gives the Selenium 4 patterns that avoid flaky scripts: Selenium Manager driver handling, explicit waits, headless mode, locators, and teardown.
Later reviews of other starred repos (e2e frameworks, crawlers) extend this skill.

## When to Use

- Driving a real browser from code: end-to-end tests, form filling, JS-heavy page scraping, screenshots, reproducing a UI bug
- Not for: static HTML scraping (`requests` + parser, or `scrapling`), calling a site's own JSON endpoints (`har-derived-api-client`), native Windows apps (`windows-desktop-e2e`)

## Facts checked (selenium 4.50.0 on Windows, Python 3.14.6)

- PyPI: `selenium` **4.50.0** (2026-09-30, Apache-2.0, Python `>=3.10`); the GitHub release tag is `selenium-4.50.0`. For comparison `playwright` 1.63.0 (2026-09-15, Apache-2.0).
- Imports and offline objects work: `webdriver.Chrome/Firefox/Edge/Safari/Remote/Ie` exist; `ChromeOptions().add_argument("--headless=new")` is stored in `.arguments`; `By` offers `ID, NAME, CLASS_NAME, TAG_NAME, CSS_SELECTOR, XPATH, LINK_TEXT, PARTIAL_LINK_TEXT`; `expected_conditions` has `presence_of_element_located`, `visibility_of_element_located`, `element_to_be_clickable`, `text_to_be_present_in_element`, `staleness_of`.
- **Selenium Manager is bundled** (`selenium/webdriver/common/windows/selenium-manager.exe`, version 0.4.50). `selenium-manager --browser chrome --offline --debug` detected the installed Chrome (`154.0.8037.93`, path under `C:\Program Files\Google\Chrome`) but logged `Unable to discover proper chromedriver version in offline mode`: **the first run needs network to fetch the matching driver** (then it is cached). Plan for that in CI and sandboxes, or pre-provision the driver and pass a `Service(executable_path=...)`.

## Patterns (documentation-sourced; Selenium docs)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

opts = webdriver.ChromeOptions()
opts.add_argument("--headless=new")                     # new headless mode, same browser as headed
opts.add_argument("--window-size=1280,800")             # responsive pages need an explicit size
driver = webdriver.Chrome(options=opts)                 # Selenium Manager resolves the driver
try:
    driver.get("https://example.org/")
    el = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1")))
    print(el.text)
    driver.save_screenshot("page.png")
finally:
    driver.quit()                                       # always: leaked drivers keep Chrome processes alive
```

- **Explicit waits, never `time.sleep`.** Wait for the condition you need (`element_to_be_clickable` before clicking). Do not mix implicit and explicit waits (the docs warn the timeouts compound unpredictably); prefer explicit only.
- Prefer stable locators: `id`, `name`, CSS selectors with data attributes (`[data-testid=...]`); avoid long absolute XPaths. After a navigation or re-render, re-find elements instead of reusing references (`StaleElementReferenceException`).
- A pytest fixture owning `driver` with `yield` + `quit()` gives one browser per test or per session; take a screenshot on failure for diagnosis.
- Use `driver.get_log`-style console capture or BiDi features only after checking the browser/driver support matrix.

## Choosing: Selenium vs Playwright

| Need | Pick |
|---|---|
| Existing Selenium Grid, Java/C#/Ruby test suites, W3C WebDriver standard, real Safari | Selenium |
| New Python/JS/TS e2e, auto-waiting, tracing, network interception, multi-browser engines bundled | Playwright (installs its own browsers; `playwright install`) |
| Quick one-off page interaction in an agent session | the built-in browser tools of the host if available; else Playwright |

## Pitfalls

- A script that "works" locally and hangs in CI is usually a missing display/headless flag or a driver download blocked by the network.
- Do not store credentials in scripts or commit browser profiles; pass secrets via environment variables.
- Respect robots.txt/terms and rate limits when scraping; automating a logged-in session is acting as that user.
- Never bypass CAPTCHAs or bot detection; if a site blocks automation, use its API or ask the owner.

## Verification

`python -c "import selenium; print(selenium.__version__)"` matches the pinned version; a smoke script loads a local file or a known page, asserts on a visible element, saves a screenshot, and exits with `driver.quit()` (check no `chromedriver`/`chrome` processes remain).
