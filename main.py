import requests
from bs4 import BeautifulSoup
from html import unescape
from collections import defaultdict

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
    header_map = {}

    # Find the first table with "x-coordinate" in the headers
    for table in tables:
        header_row = table.find("tr")
        if not header_row:
            continue
        headers = [unescape(cell.get_text(strip=True)).lower() for cell in header_row.find_all(["td", "th"])]
        if "x-coordinate" in headers:
            target_table = table
            header_map = {header: idx for idx, header in enumerate(headers)}
            break

    if not target_table:
        print("No table found with 'x-coordinate' in headers.")
        return []

    parsed_rows = []
    data_rows = target_table.find_all("tr")[1:]  # skip header

    for idx, row in enumerate(data_rows, start=1):
        cells = row.find_all(["td", "th"])
        if len(cells) != 3:
            print(f"Skipping malformed row at index {idx}: does not have exactly 3 columns")
            continue

        try:
            x_val = unescape(cells[header_map["x-coordinate"]].get_text(strip=True))
            y_val = unescape(cells[header_map["y-coordinate"]].get_text(strip=True))
            x = int(x_val)
            y = int(y_val)
        except (KeyError, ValueError) as e:
            print(f"Skipping malformed row at index {idx}: {e}")
            continue

        # Get the character from the remaining column
        try:
            char_index = next(
                i for i in range(3) if i not in (header_map["x-coordinate"], header_map["y-coordinate"])
            )
            character = unescape(cells[char_index].get_text(strip=True))
        except StopIteration:
            print(f"Skipping malformed row at index {idx}: No character column found.")
            continue

        parsed_rows.append((x, y, character))

    return parsed_rows


def render_ascii_canvas(data_tuples):
    # Group characters by y-coordinate
    rows_by_y = defaultdict(dict)
    for x, y, char in data_tuples:
        rows_by_y[y][x] = char

    if not rows_by_y:
        print("No data to render.")
        return

    max_y = max(rows_by_y.keys())
    min_y = min(rows_by_y.keys())

    for y in range(max_y, min_y - 1, -1):
        if y in rows_by_y:
            row = rows_by_y[y]
            max_x = max(row.keys())
            line = ''.join(row.get(x, ' ') for x in range(max_x + 1))
            print(line)
        else:
            print('')  # Blank line for missing y


if __name__ == "__main__":
    url = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"
    parsed_data = fetch_and_parse_table(url)
    render_ascii_canvas(parsed_data)
