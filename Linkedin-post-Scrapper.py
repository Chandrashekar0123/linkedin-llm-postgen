#login_and_save.session.py
import asyncio
from playwright.async_api import async_playwright

SESSION_FILE = "playwright-session/saved_session.json"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔐 Open LinkedIn Login Page...")
        await page.goto("https://www.linkedin.com/login")

        print("✅ Please login manually...")

        # Wait until login is successful
        await page.wait_for_url("https://www.linkedin.com/feed/", timeout=180000)

        print("💾 Saving session...")
        await context.storage_state(path=SESSION_FILE)
        print("✅ Session saved.")

        await browser.close()

asyncio.run(run())

#scrape_posts.py
from playwright.async_api import async_playwright

# File containing saved LinkedIn session cookies
SESSION_FILE = "playwright-session/saved_session.json"

async def scrape_all_posts(profile_url, scroll_pause=1000, max_posts=50):
    """
    Scrapes up to `max_posts` posts from a LinkedIn profile's activity page.

    Args:
        profile_url (str): LinkedIn profile URL (e.g., 'https://www.linkedin.com/in/username/').
        scroll_pause (int): Delay between scroll actions in milliseconds.
        max_posts (int): Maximum number of posts to scrape.

    Returns:
        list: A list of extracted post texts.
    """
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        
        # Load saved LinkedIn session
        context = await browser.new_context(storage_state=SESSION_FILE)
        page = await context.new_page()

        print("📄 Opening profile...")

        # Ensure we are on the activity page (all posts)
        if '/in/' in profile_url and not profile_url.endswith('/recent-activity/all/'):
            activity_url = profile_url.rstrip('/') + '/recent-activity/all/'
        else:
            activity_url = profile_url

        await page.goto(activity_url)

        print("🔄 Scrolling to load posts (up to max limit)...")
        previous_count = -1
        same_count_times = 0

        while True:
            # Scroll down
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(scroll_pause)

            # Count currently loaded posts
            posts = await page.locator("div.feed-shared-update-v2").all()
            current_count = len(posts)

            # Stop if reached max_posts
            if current_count >= max_posts:
                break

            # Stop if no new posts appear after several scrolls
            if current_count == previous_count:
                same_count_times += 1
                if same_count_times >= 3:
                    break
            else:
                same_count_times = 0

            previous_count = current_count

        # Limit to `max_posts` in extraction
        posts = posts[:max_posts]
        print(f"📦 Found {len(posts)} posts. Extracting text...")

        # Extract unique post texts
        post_texts = []
        for post in posts:
            try:
                text = await post.locator("span.break-words").text_content()
                if text:
                    clean_text = text.strip()
                    if clean_text and clean_text not in post_texts:
                        post_texts.append(clean_text)
            except:
                pass  # Ignore posts without text content

        await browser.close()
        return post_texts


#scrape_profile.py
from playwright.async_api import async_playwright

SESSION_FILE = "playwright-session/saved_session.json"

async def scrape_profile_data(profile_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=SESSION_FILE)
        page = await context.new_page()
        await page.goto(profile_url)

        print("🔍 Scraping profile info...")

        name = await page.locator("h1").text_content()
        title = await page.locator("div.text-body-medium.break-words").first.text_content()
        location = await page.locator("span.text-body-small.inline.t-black--light.break-words").first.text_content()

        profile = {
            "Name": name.strip() if name else "",
            "Title": title.strip() if title else "",
            "Location": location.strip() if location else ""
        }

        await browser.close()
        return profile
#main.py
import asyncio
import json
import csv
import os
from datetime import datetime
from scrape_profile import scrape_profile_data
from scrape_posts import scrape_all_posts  # ✅ updated import

# File paths for data storage
JSON_FILE = "linkedin_data.json"
CSV_FILE = "linkedin_data.csv"

async def process_profile(url):
    url = url.strip()
    if not url:
        return

    print(f"\n🔗 Processing: {url}")
    print("🔎 Scraping Profile Info...")
    profile = await scrape_profile_data(url)
    print("\n📋 Profile Information:")
    for k, v in profile.items():
        print(f"{k}: {v}")

    print("\n📰 Scraping All Posts...")  # updated wording
    posts = await scrape_all_posts(url)  # ✅ call updated function
    for i, post in enumerate(posts, 1):
        print(f"\nPost {i}:\n{post}")
    
    scraped_data = {
        "url": url,
        "profile": profile,
        "posts": posts,
        "scraped_at": datetime.now().isoformat(),
        "profile_id": extract_profile_id(url)
    }

    save_to_json(scraped_data)
    save_to_csv(scraped_data)
    print(f"\n💾 Data saved for {url} to {JSON_FILE} and {CSV_FILE}")

async def main():
    print("Enter LinkedIn Profile URLs (comma-separated or one per line). Type 'done' to finish input:")
    urls = []
    while True:
        line = input().strip()
        if line.lower() == 'done':
            break
        if ',' in line:
            urls.extend([u.strip() for u in line.split(',') if u.strip()])
        elif line:
            urls.append(line)
    
    # Process each profile URL one by one
    for url in urls:
        await process_profile(url)

def extract_profile_id(url):
    try:
        if '/in/' in url:
            return url.split('/in/')[-1].rstrip('/')
        return "unknown"
    except:
        return "unknown"

def save_to_json(new_data):
    existing_data = []
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []

    profile_exists = False
    for i, item in enumerate(existing_data):
        if item.get('url') == new_data['url'] or item.get('profile_id') == new_data['profile_id']:
            existing_data[i] = new_data
            profile_exists = True
            print("✅ Updated existing profile in JSON")
            break

    if not profile_exists:
        existing_data.append(new_data)
        print("✅ Added new profile to JSON")

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

def save_to_csv(new_data):
    file_exists = os.path.exists(CSV_FILE)
    existing_rows = []

    if file_exists:
        try:
            with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                existing_rows = list(reader)
        except FileNotFoundError:
            existing_rows = []

    new_rows = convert_to_csv_format(new_data)
    profile_id = new_data['profile_id']
    existing_rows = [row for row in existing_rows if row.get('Profile_ID') != profile_id]
    existing_rows.extend(new_rows)

    headers = [
        'Profile_ID', 'URL', 'Name', 'Title', 'Location', 'Scraped_At', 
        'Type', 'Content', 'Post_Number', 'Word_Count', 'Character_Count'
    ]

    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(existing_rows)

    if file_exists:
        print("✅ Updated existing data in CSV")
    else:
        print("✅ Created new CSV file with data")

def convert_to_csv_format(data):
    rows = []
    profile_row = {
        'Profile_ID': data['profile_id'],
        'URL': data['url'],
        'Name': data['profile'].get('Name', ''),
        'Title': data['profile'].get('Title', ''),
        'Location': data['profile'].get('Location', ''),
        'Scraped_At': data['scraped_at'],
        'Type': 'Profile',
        'Content': '',
        'Post_Number': '',
        'Word_Count': '',
        'Character_Count': ''
    }
    rows.append(profile_row)

    for i, post in enumerate(data['posts'], 1):
        post_row = {
            'Profile_ID': data['profile_id'],
            'URL': data['url'],
            'Name': data['profile'].get('Name', ''),
            'Title': data['profile'].get('Title', ''),
            'Location': data['profile'].get('Location', ''),
            'Scraped_At': data['scraped_at'],
            'Type': 'Post',
            'Content': post,
            'Post_Number': i,
            'Word_Count': len(post.split()),
            'Character_Count': len(post)
        }
        rows.append(post_row)

    return rows

if __name__ == "__main__":
    asyncio.run(main())
