from playwright.sync_api import sync_playwright

url = "https://music.yandex.ru/users/nicholas28/playlists/1113"
output_file = "Live Chill Rave Meditation.txt"
user_data_dir = "/Users/nikolay/Library/Application Support/Google/Chrome"


with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
    )
    page = browser.new_page()
    page.goto(url, timeout=60000)
    page.wait_for_selector('[aria-label]', timeout=30000)

    track_labels = page.eval_on_selector_all(
        '[aria-label]',
        "elements => elements.map(e => e.getAttribute('aria-label'))"
    )
    track_labels = list(dict.fromkeys(track_labels))

    with open(f"playlists/{output_file}", "w") as f:
        for track in track_labels:
            f.write(track.strip() + "\n")

    print(f"Saved {len(track_labels)} tracks to playlists/{output_file}")

    browser.close()
