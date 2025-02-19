import requests
import json
import time

def fetch_notion_content(database_id, token):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching content: {response.json()}")
    return response.json()

def create_notion_page(page_data, token):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.post(url, headers=headers, data=json.dumps(page_data))
    if response.status_code != 200:
        print(f"Error creating page: {response.status_code}, {response.json()}")
    return response.json()

def transfer_data(origin_db_id, dest_db_id, origin_token, dest_token):
    # Fetch data from the original account
    content = fetch_notion_content(origin_db_id, origin_token)

    if not content.get('results'):
        print(f"No content found in the database with ID {origin_db_id}.")
        return

    print(f"Fetched {len(content['results'])} items from original database.")

    # Prepare and create new pages in the destination database
    for item in content['results']:
        page_data = {
            "parent": {"database_id": dest_db_id},
            "properties": item["properties"],
            "children": item.get("children", [])
        }

        # Log the page data for debugging purposes
        print(f"Creating page with data: {json.dumps(page_data, indent=2)}")

        # Create the page in the destination database
        response = create_notion_page(page_data, dest_token)

        # Check for rate limiting
        if response.get("object") == "error" and response.get("status") == 429:
            wait_time = int(response.headers.get("Retry-After", 1))
            print(f"Rate limit hit. Retrying after {wait_time} seconds.")
            time.sleep(wait_time)
            response = create_notion_page(page_data, dest_token)

        if response.get("object") == "error":
            print(f"Error creating page: {response}")
        else:
            print(f"Successfully created page with ID {response['id']}")

if __name__ == "__main__":
    origin_db_id = input("Enter the origin Notion database ID: ")
    dest_db_id = input("Enter the destination Notion database ID: ")
    origin_token = input("Enter the origin account API token: ")
    dest_token = input("Enter the destination account API token: ")

    transfer_data(origin_db_id, dest_db_id, origin_token, dest_token)