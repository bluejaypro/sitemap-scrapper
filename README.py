# sitemap-scrapper
scrap sitemap and check internal links
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import re

# Function to crawl the website and collect internal URLs
def crawl_website(base_url, max_urls=100, headers=None):
    visited_urls = set()  # Set to track visited URLs
    url_map = defaultdict(set)  # Dictionary to store which pages link to which others
    orphan_pages = set()  # To store orphan pages (no incoming links)

    def scrape_page(url):
        """Scrape a single page, extract all internal links, and track them."""
        nonlocal visited_urls, url_map, orphan_pages

        # If we have reached the max URL limit, stop
        if len(visited_urls) >= max_urls:
            return

        # Skip already visited URLs
        if url in visited_urls:
            return

        visited_urls.add(url)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(f"An error occurred while scraping {url}: {err}")
            return

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all internal links
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)  # Convert relative URL to absolute

            # Only consider internal links (same domain)
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                # Add to the url_map for tracking which page links to which
                url_map[absolute_url].add(url)

        # Identify orphan pages by checking which pages have no incoming links
        for linked_page in url_map:
            if url not in url_map[linked_page]:
                orphan_pages.add(url)

    # Start scraping from the base URL
    scrape_page(base_url)

    # Return all visited URLs and orphan pages
    return visited_urls, orphan_pages, url_map

# Function to analyze the internal link structure
def analyze_internal_links(base_url, max_urls=500, headers=None):
    # Crawl the website to gather all URLs and the internal linking structure
    visited_urls, orphan_pages, url_map = crawl_website(base_url, max_urls, headers)

    print("\n--- All Visited URLs ---")
    for url in visited_urls:
        print(url)

    print("\n--- Orphan Pages (Pages not linked to by any other page) ---")
    for orphan in orphan_pages:
        print(orphan)

    print("\n--- Internal Links Structure (Who links to whom) ---")
    for url, links in url_map.items():
        print(f"Page: {url}")
        print("Links to:")
        for link in links:
            print(f"  - {link}")
        print()

# Main execution example
if __name__ == "__main__":
    base_url = "https://drwattselectric.com/"  # Replace with your site URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Call the analysis function
    analyze_internal_links(base_url, max_urls=500, headers=headers)
