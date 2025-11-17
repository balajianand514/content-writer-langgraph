import requests

def bing_search(query, sites):
    # Replace with your own values
    subscription_key = 'ff129867b827491aa4279728cd810b8f'
    endpoint = 'https://api.bing.microsoft.com/v7.0/search'

    # Create a query with specific sites
    site_filter = ' OR '.join([f'site:{site}' for site in sites])
    search_query = f"{query} {site_filter}"

    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params = {'q': search_query, 'textDecorations': True, 'textFormat': 'HTML'}

    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Example usage
if __name__ == '__main__':
    query = "latest technology trends"
    websites = ["example.com", "hbr.org", "forbes.com"]
    
    results = bing_search(query, websites)

    if results:
        # Process and print the results
        for i, result in enumerate(results.get('webPages', {}).get('value', [])):
            print(f"{i + 1}. {result['name']}: {result['url']}")
            print(f"Snippet: {result['snippet']}\n")
