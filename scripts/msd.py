import json
import re
from tqdm import tqdm
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from time import time

def get_info_and_texts_from_single_article(url, breadcrumb_class="breadcrumb__link", article_class="topic__article"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape breadcrumb links
        elements = soup.find_all('a', class_=breadcrumb_class)
        if len(elements) >= 4:
            # Remove leading digits and space from the text in elements[1]
            topic_text = re.sub(r'^\d+\.\s+', '', elements[1].get_text(strip=True))

            breadcrumb_texts = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "link": url,
                "topic": topic_text,
                "category": elements[2].get_text(strip=True),
                "title": elements[3].get_text(strip=True)
            }
        else:
            breadcrumb_texts = "Not enough breadcrumb links found."

        # Extract article text
        article_element = soup.find(class_=article_class)
        if article_element:
            article_text = article_element.get_text(strip=True)
        else:
            article_text = "Article text not found."

        combined_data = {
            **breadcrumb_texts,
            "text": article_text
        }

        # Save as JSON
        json_filename = '/home/nagashimadaichi/develop/assets/msd_combined.json'  # Your specified path
        with open(json_filename, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, ensure_ascii=False)

        return combined_data
    except requests.RequestException as e:
        return "An error occurred: " + str(e)


# get links from category page
def get_links_from_category_page(url, class_name="medicalsection__section") -> list[str]:
    try:
        response = requests.get(url)
        response.raise_for_status()  # This raises an exception for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        sections = soup.find_all(class_=class_name)

        all_links = []
        for section in sections:
            links = section.find_all('a')
            for link in links:
                full_link = urljoin(url, link.get('href'))
                all_links.append(full_link)
        
        return all_links
    except requests.RequestException as e:
        return "An error occurred: " + str(e)


# get links from clinical department
def get_links_from_topics_page(url, class_name="section__item") -> list[str]:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all('a', class_=class_name)

        links = [urljoin(url, element.get('href')) for element in elements]
        return links
    except requests.RequestException as e:
        return "An error occurred: " + str(e)

def scrape_all_data(base_url, json_path="/home/nagashimadaichi/develop/assets/msd.json"):
    topic_links = get_links_from_topics_page(base_url)
    all_article_data = []

    # 各トピックのカテゴリーリンクを取得し、合計数を計算
    total_category_links = 0
    for topic_link in topic_links:
        category_links = get_links_from_category_page(topic_link)
        total_category_links += len(category_links)

    progress_bar = tqdm(total=total_category_links, desc="Processing Articles")

    for topic_link in topic_links:
        category_links = get_links_from_category_page(topic_link)

        for category_link in category_links:
            try:
                article_data = get_info_and_texts_from_single_article(category_link)
                all_article_data.append(article_data)
                print(f"Completed processing article: {category_link}")
            except requests.RequestException as e:
                print(f"An error occurred while processing {category_link}: {e}")
            finally:
                progress_bar.update(1)  # Update the progress bar
                time.sleep(5)  # 5秒待機してから次の記事に進む

    progress_bar.close()  # Close the progress bar

    # Save all article data to a single JSON file
    combined_json_filename = json_path
    with open(combined_json_filename, 'w', encoding='utf-8') as file:
        json.dump(all_article_data, file, ensure_ascii=False)

    return f"All data saved. Total articles: {len(all_article_data)}"



if __name__ == "__main__":

    #BASE_URL = "https://www.msdmanuals.com/ja-jp/%E3%83%97%E3%83%AD%E3%83%95%E3%82%A7%E3%83%83%E3%82%B7%E3%83%A7%E3%83%8A%E3%83%AB/health-topics"  
    #result = scrape_all_data(BASE_URL)