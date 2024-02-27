import asyncio
import httpx
import json
from time import perf_counter
from aiolimiter import AsyncLimiter


async def log_request(request):
    print(f"Request: {request.url!r} {request.method!r}")


async def log_response(response):
    print(f"Response: {response.url!r} {response.status_code!r}")


async def get_branch():
    cookies = {
        'eael_screen': '1280',
        'cookielawinfo-checkbox-necessary': 'yes',
        'cookielawinfo-checkbox-functional': 'no',
        'cookielawinfo-checkbox-performance': 'no',
        'cookielawinfo-checkbox-analytics': 'no',
        'cookielawinfo-checkbox-advertisement': 'no',
        'cookielawinfo-checkbox-others': 'no',
        'CookieLawInfoConsent': 'eyJuZWNlc3NhcnkiOnRydWUsImZ1bmN0aW9uYWwiOmZhbHNlLCJwZXJmb3JtYW5jZSI6ZmFsc2UsImFuYWx5dGljcyI6ZmFsc2UsImFkdmVydGlzZW1lbnQiOmZhbHNlLCJvdGhlcnMiOmZhbHNlfQ==',
        'viewed_cookie_policy': 'yes',
    }

    headers = {
        'authority': 'www.dolex.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,en-GB;q=0.8,de;q=0.7,es;q=0.6',
        'dnt': '1',
        'referer': 'https://www.dolex.com/branches-products-services/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'action': 'asl_load_stores',
        'lang': '',
        'nonce': '757027776f',
        'load_all': '1',
        'layout': '1',
    }
    all_branch_list = []
    key_branch_list = []
    cali_branch_list = []

    url = 'https://www.dolex.com/wp-admin/admin-ajax.php'

    # Create an AsyncLimiter instance
    limiter = AsyncLimiter(10)
    # Use the limiter to limit the number of concurrent requests
    async with limiter:
        async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}, headers=headers, cookies=cookies, timeout=60.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                if content_type := response.headers.get('Content-Type', '').lower():
                    if 'text/html' in content_type:
                        data = response.json()
                        # Extract the branch data
                        all_branch_list.extend(data)
                        # Cache the JSON output to a file
                        with open(f'branch_data.json', 'w') as f:
                            json.dump(data, f, indent=4)
                            print(f"Data cached to branch_data.json")
                        # Using the JSON output, extract the branch title, street, city, state and postal code only where state is 'California'.
                        for branch in data:
                            if branch['state'] == 'California':
                                StoreName = branch['title']
                                Address = branch['street']
                                CityName = branch['city']
                                State = branch['state']
                                ZipCode = branch['postal_code']
                                cali_branch_list.append(f"{StoreName}, {Address}, {CityName}, {State}, {ZipCode}")

                        # Save the cali_branch_list to a file
                        with open('cali_branch_list.txt', 'w') as f:
                            for branch in cali_branch_list:
                                f.write(f'{branch}\n')
                        # prints the length of the list
                        print("Length of CALI BRANCHES: ", len(cali_branch_list))
                    else:
                        print(f"Received error response: {response.status_code}")
                else:
                    print("No Content-Type header received")
            else:
                print(f"Received error response: {response.status_code}")
        # Save the branch_list to a file
        with open('branch_list.txt', 'w') as f:
            for branch in all_branch_list:
                f.write(f'{branch}\n')
        # prints the length of the list
        print("Length of ALL BRANCHES: ", len(all_branch_list))
        return all_branch_list


async def main():
    start = perf_counter()
    await get_branch()
    finish = perf_counter()
    print(f'Finished in {round(finish-start, 2)} second(s)')

if __name__ == '__main__':
    asyncio.run(main())
