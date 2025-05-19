import requests
from bs4 import BeautifulSoup
from html import unescape

def fetch_and_parse_table(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch the document: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")

    target_table = None
    for table in tables:
        headers = table.find_all("tr")[0].find_all(["td", "th"])
        headers_text = [unescape(cell.get_text(strip=True)) for cell in headers]
        if "x-coordinate" in headers_text:
            target_table = table
            break

    if not target_table:
        print("No table found with 'x-coordinate' in headers.")
        return []

    parsed_rows = []
    header_cells = target_table.find_all("tr")[0].find_all(["td", "th"])
    headers = [unescape(cell.get_text(strip=True)) for cell in header_cells]

    for idx, row in enumerate(target_table.find_all("tr")[1:], start=1):  # Skip header row
        cells = row.find_all(["td", "th"])
        if len(cells) != 3:
            print(f"Skipping malformed row at index {idx}: does not have exactly 3 columns")
            continue

        values = []
        malformed = False
        for i, cell in enumerate(cells):
            text = unescape(cell.get_text(strip=True))
            header = headers[i].lower()
            if header in ("x-coordinate", "y-coordinate"):
                try:
                    values.append(int(text))
                except ValueError:
                    print(f"Skipping malformed row at index {idx}: '{header}' is not an integer")
                    malformed = True
                    break
            else:
                values.append(text)

        if not malformed:
            parsed_rows.append(tuple(values))

    return parsed_rows

if __name__ == "__main__":
    url = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"
    result = fetch_and_parse_table(url)
    print("\nParsed table data:")
    for row in result:
        print(row)
