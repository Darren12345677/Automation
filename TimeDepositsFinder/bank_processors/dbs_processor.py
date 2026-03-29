DBS_URL = "https://www.dbs.com.sg/personal/rates-online/singapore-dollar-fixed-deposits.page"
DBS_NAME = "DBS"

def dbs_processor(page):
    tables = page.locator("table").all()
    target_table = None

    # Find correct table using header text
    for table in tables:
        headers = table.locator("th").all_text_contents()
        headers = [h.strip() for h in headers]

        if len(headers) > 0 and headers[0] == "Period":
            target_table = table
            break

    if target_table is None:
        raise Exception("Could not find the tiered FD table")

    # Extract headers (amount tiers)
    headers = target_table.locator("th").all_text_contents()
    headers = [h.strip() for h in headers]

    rows = target_table.locator("tbody tr").all()

    data = []

    for row in rows:
        cols = row.locator("td").all_text_contents()
        cols = [c.strip() for c in cols]

        if len(cols) != len(headers):
            continue

        row_data = {
            "period": cols[0]
        }

        # Map each tier dynamically
        for i in range(1, len(headers)):
            row_data[headers[i]] = float(cols[i])

        data.append(row_data)

    return data


