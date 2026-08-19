import asyncio
from playwright.async_api import async_playwright
import json

async def fetch_real_jobs():
    discovered = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        
        # 1. Workable
        print("[*] Scraping Workable for 'gohighlevel'...")
        try:
            await page.goto("https://jobs.workable.com/search?query=gohighlevel", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            cards = await page.query_selector_all("li[data-ui='job-card'], a[href*='/view/']")
            print(f"Found {len(cards)} cards on Workable")
            for c in cards:
                href = await c.get_attribute("href")
                if not href:
                    a = await c.query_selector("a[href*='/view/']")
                    if a:
                        href = await a.get_attribute("href")
                
                title_el = await c.query_selector("h3, strong, [data-ui='job-title']")
                title = await title_el.inner_text() if title_el else ""
                
                comp_el = await c.query_selector("p, [data-ui='company-name']")
                comp = await comp_el.inner_text() if comp_el else "Remote Agency"
                
                if href:
                    full_url = f"https://jobs.workable.com{href}" if href.startswith("/") else href
                    discovered.append({
                        "title": title or "GoHighLevel Specialist",
                        "company": comp or "Workable Partner",
                        "url": full_url,
                        "source": "Workable"
                    })
        except Exception as e:
            print(f"Workable scrape error: {e}")

        await browser.close()

    print(f"\nTotal Discovered Real Live Jobs: {len(discovered)}")
    for d in discovered:
        print(f" - {d['title']} @ {d['company']} -> {d['url']}")

if __name__ == "__main__":
    asyncio.run(fetch_real_jobs())
