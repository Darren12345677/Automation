
CIMB_URL = "https://www.cimb.com.sg/en/personal/help-support/rates-charges/rates/sgd-fixed-deposit-rates.html"
CIMB_NAME = "CIMB"

def cimb_processor(page):
        # Find the correct table using header text
        tables = page.locator("table").all()

        target_table = None

        for table in tables:
            header_text = table.inner_text()

            if "TENURE" in header_text and "PERSONAL BANKING" in header_text:
                target_table = table
                break

        if target_table is None:
            raise Exception("Could not find the FD rates table")

        rows = target_table.locator("tr").all()

        data = []

        for row in rows[1:]:
            cols = row.locator("td").all_text_contents()

            if len(cols) >= 3:
                data.append({
                    "tenure": cols[0].strip(),
                    "personal_rate": float(cols[1].strip()),
                    "preferred_rate": float(cols[2].strip())
                })

        
        return data