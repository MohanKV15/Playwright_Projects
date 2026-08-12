with open("debug_loni.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
m = re.search(r"Lot/Development/Frontage Information", content)
if m:
    print("--- Lot/Development/Frontage Information SECTION ---")
    print(content[m.start():m.end() + 3000])
else:
    print("Not found")

