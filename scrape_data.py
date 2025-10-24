import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import mysql.connector
import requests
from bs4 import BeautifulSoup
import pandas as pd

import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Base URL of the search page (with the scope parameter)
base_url = 'https://www.opensanctions.org/search/'

# Initialize lists to store extracted data
names = []
types = []
categories = []
nationalities = []

# Set initial offset value and the maximum number of pages to scrape
offset = 0
max_offset = 10000  # Adjust this as needed, based on the total number of records you want to scrape
scope = 'ae_local_terrorists'  # The scope filter in the URL

while offset < max_offset:
    # Construct the URL with the current offset and scope
    url = f"{base_url}?offset={offset}&scope={scope}"
    print(f"Scraping page with offset: {offset}")

    # Send GET request to the current page
    response = requests.get(url)
    coverpage = response.content

    # Parse the page content with BeautifulSoup
    soap = BeautifulSoup(coverpage, 'html5lib')

    # Find all the search result items (list of entities)
    all_search_items = soap.find_all('li', class_='Search_resultItem__RNdvE')

    # If no items are found, break the loop (end of pagination)
    if not all_search_items:
        print("No more results, ending scraping.")
        break

    # Loop through each search result item on the current page
    for item in all_search_items:
        # Extract the name of the person/entity
        name = item.find('div', class_='Search_resultTitle__twair').get_text(strip=True)
        names.append(name)
        
        # Extract the type of the entity (e.g., "Person", "Company")
        entity_type = item.find('p', class_='Search_resultDetails__13RZP').find('span', class_='badge bg-light').get_text(strip=True)
        types.append(entity_type)
        
        # Extract the categories (e.g., "Close Associate", "Politician", etc.)
        category_tags = item.find('p', class_='Search_resultDetails__13RZP').find_all('span', class_='badge bg-warning')
        categories_text = [category.get_text(strip=True) for category in category_tags]
        categories.append(", ".join(categories_text))  # Join multiple categories if they exist
        
        # Extract nationality or country
        nationality = item.find('p', class_='Search_resultDetails__13RZP').find_all('span')[-1].get_text(strip=True)
        nationalities.append(nationality)

    # Increment offset for the next page
    offset += 25

# Create a PDF file
pdf_filename = "opensanctions_data.pdf"
c = canvas.Canvas(pdf_filename, pagesize=letter)
width, height = letter  # Default size is 612x792 points (8.5x11 inches)

# Set initial position for writing the text
x = 40
y = height - 40  # Start from the top of the page

# Set a line height for the data
line_height = 14

# Title
c.setFont("Helvetica-Bold", 16)
c.drawString(x, y, "OpenSanctions Data")
y -= 20

# Loop through the extracted data and write it to the PDF
c.setFont("Helvetica", 10)
for i in range(len(names)):
    if y < 40:  # Check if we need to create a new page
        c.showPage()
        c.setFont("Helvetica", 10)
        y = height - 40  # Reset the vertical position

    # Write the name, type, categories, and nationality to the PDF
    c.drawString(x, y, f"Name: {names[i]}")
    y -= line_height
    c.drawString(x, y, f"Type: {types[i]}")
    y -= line_height
    c.drawString(x, y, f"Categories: {categories[i]}")
    y -= line_height
    c.drawString(x, y, f"Nationality: {nationalities[i]}")
    y -= line_height

    # Add a separator line
    c.drawString(x, y, "-" * 80)
    y -= 20  # Extra space after separator

# Save the PDF
c.save()

print(f"Data has been saved to '{pdf_filename}'.")
