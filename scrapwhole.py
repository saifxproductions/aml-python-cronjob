import requests
from bs4 import BeautifulSoup
import time

# Base URL for the search page
base_url = 'https://www.opensanctions.org/search/?offset='
scope = 'ae_local_terrorists'  # Adjust the scope if needed
output_txt = 'opensanctions_data.txt'

# Function to scrape person URLs from a search result page
def scrape_person_urls(page_offset):
    url = f"{base_url}{page_offset}&scope={scope}"
    print(f"Scraping page: {url}")
    
    # Send GET request to the search page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the person profile links (hrefs) on the page
    person_links_on_page = soup.find_all('a', href=True)

    person_urls = []
    # Extract relevant profile URLs (those that match the pattern for persons)
    for link in person_links_on_page:
        if link['href'].startswith('/entities/'):
            full_url = 'https://www.opensanctions.org' + link['href']
            person_urls.append(full_url)

    # Check if there is a "next page" link to scrape more pages
    next_page = soup.find('li', class_='pagination_next')
    if next_page and next_page.find('a'):
        return person_urls, True  # More pages to scrape
    return person_urls, False

# Function to extract detailed data from each person's profile
def extract_person_data(person_url):
    response = requests.get(person_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the factsheet table containing the person's details
    table = soup.find('table', class_='Entity_factsheet__EG_nj table')
    if not table:
        print(f"No factsheet found for {person_url}")
        return None

    data = {}
    
    # Extracting rows from the factsheet table
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1:
            header = row.find('th').get_text(strip=True)
            value = cols[0].get_text(strip=True)
            data[header] = value

    return data

# Function to save the data to a text file
def save_to_text_file(person_data):
    with open(output_txt, 'a', encoding='utf-8') as f:  # Open file in 'append' mode
        for data in person_data:
            f.write(f"Name: {data['Name']}\n")
            for key, value in data.items():
                if key != 'Name':  # Skip the name since it's already printed
                    f.write(f"{key}: {value}\n")
            f.write("\n" + "-" * 80 + "\n\n")

    print(f"Data for {len(person_data)} profiles has been saved to '{output_txt}'.")

# Scrape the paginated list of persons (we'll start at offset 0 and loop through pages)
page_offset = 0
all_person_urls = []

# Loop to scrape all pages and collect person URLs
while True:
    # Scrape current page and get the person URLs
    person_urls_on_page, has_more_pages = scrape_person_urls(page_offset)
    all_person_urls.extend(person_urls_on_page)  # Add the scraped URLs to the list
    
    # If there's a "next page", continue scraping
    if not has_more_pages:
        break
    
    # Move to the next page (next offset)
    page_offset += 25
    
    # Pause between page requests to avoid overwhelming the server
    time.sleep(2)

# After collecting all person URLs, now scrape each person's detailed data
all_person_data = []

# Loop through all collected person URLs and extract data
for person_url in all_person_urls:
    data = extract_person_data(person_url)
    if data:
        # Add 'URL' to the data for context
        data['URL'] = person_url
        all_person_data.append(data)
    
    # Pause to avoid overwhelming the server with requests
    time.sleep(2)

# Save the collected data to a text file
if all_person_data:
    save_to_text_file(all_person_data)

# After scraping, notify completion
print("All data has been scraped and saved to the text file.")


# import requests
# from bs4 import BeautifulSoup
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# import time

# # Base URL for the search page
# base_url = 'https://www.opensanctions.org/search/?offset='
# scope = 'ae_local_terrorists'  # Adjust the scope if needed
# output_pdf = 'opensanctions_data.pdf'

# # Initialize lists to store extracted data
# names = []
# links = []

# # Function to scrape the list of persons from a page
# def scrape_person_list(page_offset):
#     url = f"{base_url}{page_offset}&scope={scope}"
#     print(f"Scraping page: {url}")
    
#     # Send GET request to the search page
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Find all the person profile links (hrefs) on the page
#     person_links = soup.find_all('a', href=True, text=True)

#     # Extract relevant profile URLs (those that match the pattern for persons)
#     for link in person_links:
#         if link['href'].startswith('/entities/'):
#             full_url = 'https://www.opensanctions.org' + link['href']
#             names.append(link.text.strip())
#             links.append(full_url)

#     # Check if we need to move to the next page
#     next_page = soup.find('li', class_='pagination_next')
#     if next_page and next_page.find('a'):
#         return True  # More pages to scrape
#     return False

# # Function to extract data from each person's profile page
# def extract_person_data(person_url):
#     response = requests.get(person_url)
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Find the factsheet table containing the person's details
#     table = soup.find('table', class_='Entity_factsheet__EG_nj table')
#     if not table:
#         print(f"No factsheet found for {person_url}")
#         return None

#     data = {}
    
#     # Extracting the rows from the factsheet table
#     rows = table.find_all('tr')
#     for row in rows:
#         cols = row.find_all('td')
#         if len(cols) > 1:
#             header = row.find('th').get_text(strip=True)
#             value = cols[0].get_text(strip=True)
#             data[header] = value

#     return data

# # Function to generate PDF from the extracted data
# def generate_pdf(person_data):
#     c = canvas.Canvas(output_pdf, pagesize=letter)
#     width, height = letter  # Default size is 612x792 points (8.5x11 inches)

#     x = 40
#     y = height - 40  # Start from the top of the page
#     line_height = 14

#     # Set title
#     c.setFont("Helvetica-Bold", 16)
#     c.drawString(x, y, "OpenSanctions Data")
#     y -= 20

#     c.setFont("Helvetica", 10)
#     for data in person_data:
#         if y < 40:  # Start a new page if space is running out
#             c.showPage()
#             c.setFont("Helvetica", 10)
#             y = height - 40

#         # Write the person's name and their profile details
#         c.drawString(x, y, f"Name: {data['Name']}")
#         y -= line_height
#         for key, value in data.items():
#             if key != 'Name':  # Skip the name since it's already printed
#                 c.drawString(x, y, f"{key}: {value}")
#                 y -= line_height

#         y -= 10  # Extra space after each profile
#         c.drawString(x, y, "-" * 80)
#         y -= 20

#     c.save()
#     print(f"Data has been saved to '{output_pdf}'.")

# # Scrape the paginated list of persons (we'll start at offset 0 and loop through pages)
# page_offset = 0
# person_data = []

# while True:
#     has_more_pages = scrape_person_list(page_offset)
#     if not has_more_pages:
#         break
#     page_offset += 25  # Increase offset to get to the next page
    
#     # Pause to avoid overwhelming the server with requests
#     time.sleep(2)

# # Now, extract profile data for each person and store it in the person_data list
# for link in links:
#     data = extract_person_data(link)
#     if data:
#         person_data.append(data)
    
#     # Pause to avoid overwhelming the server with requests
#     time.sleep(2)

# # Generate the PDF with all the collected person data
# generate_pdf(person_data)

# print("All data has been scraped and saved to the PDF.")
