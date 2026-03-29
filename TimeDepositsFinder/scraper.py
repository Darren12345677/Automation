from playwright.sync_api import sync_playwright
from bank_processors.cimb_processor import *
from bank_processors.dbs_processor import *
from bank_processors.citi_processor import *

BANK_CONFIGS = [
    (DBS_NAME, DBS_URL, dbs_processor), 
    (CIMB_NAME, CIMB_URL, cimb_processor),
    (CITIBANK_NAME, CITIBANK_URL, citibank_processor)]


def scrape(URL, bank_processor):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        # Wait for ALL tables to load
        page.wait_for_selector("table")

        results = bank_processor(page)

        browser.close()
    return results

def main():
    for bank_config in BANK_CONFIGS: 
        bank_name, bank_url, bank_processor = bank_config
        header = ["=" * 20, bank_name, ""]
        print("\n".join(header))
        print(scrape(bank_url, bank_processor))
        print("="*20)


if __name__ == "__main__":
    main()