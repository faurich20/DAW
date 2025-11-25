url = "https://jsonplaceholder.typicode.com/posts/1"

try:
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()

    print(json_data)
    print(f"Title: {json_data['title']}")
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
except ValueError as e:
    print(f"Error parsing JSON: {e}")