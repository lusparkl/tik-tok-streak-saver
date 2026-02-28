from playwright.sync_api import sync_playwright
import json

def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = browser.new_page()
        page.goto("https://github.com")
        page.wait_for_timeout(5000)
        res = input("y/n")
        if res == "y":
            page.wait_for_timeout(10000)
            cookies = page.context.cookies()
            with open('cookies.json', 'w') as f:
                json.dump(cookies, f)
                browser.close()

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
        page = browser.new_page()
        context = page.context
        context.add_cookies(cookies)
        page.wait_for_timeout(1000)
        page.goto("https://github.com")
        page.wait_for_timeout(10000)

test_login()