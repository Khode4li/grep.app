from bs4 import BeautifulSoup
import typer
import requests
import json
from concurrent.futures import ThreadPoolExecutor

PROXIES = {
    "http": "http://127.0.0.1:8080",  # Burpsuite proxy
    "https": "http://127.0.0.1:8080",
}


def get_all_source_code_ids(params):
    source_ids = []
    prev_resp = ""
    counter = 1
    while True:
        src_list = requests.get(
            f'https://grep.app/api/search?page={counter}',
            params=params,
            proxies=PROXIES,
            verify=False,
        )
        if src_list.status_code != 200:
            exit("Something went wrong!")
        if prev_resp == src_list.text[:-27]:
            break
        prev_resp = src_list.text[:-27]
        counter += 1
        json_data = json.loads(src_list.text)
        for src in json_data['hits']['hits']:
            source_ids.append(src['id']['raw'])
    return source_ids


def print_clean_source_code(src):
    soup = BeautifulSoup(src, 'html.parser')
    pre_tags = soup.find_all('pre')
    # Combine all text from <pre> tags
    full_source_code = "\n".join(pre.get_text() for pre in pre_tags)
    print(full_source_code)


def get_source_code(source_id, params):
    params['id'] = source_id
    r = requests.get(
        'https://grep.app/api/file',
        params=params,
        proxies=PROXIES,
        verify=False,
    )
    if r.status_code != 200:
        print(f"Error fetching source code for ID {source_id}.")
        return
    print_clean_source_code(r.text)


def fetch_all_source_codes_concurrently(source_ids, params, threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:  # Adjust `max_workers` as needed
        futures = [executor.submit(get_source_code, source_id, params) for source_id in source_ids]
        for future in futures:
            future.result()  # Wait for all threads to complete


app = typer.Typer()

@app.command()
def search(search: str, regex: bool = False, regexp: bool = False, lang: str = "", threads: int = 10):
    """Just a simple tool to extract source codes from grep.app"""
    params = {'q': search}
    if regexp:
        params['regexp'] = regexp
    if lang:
        params['f.lang'] = lang
    
    source_ids = get_all_source_code_ids(params)
    fetch_all_source_codes_concurrently(source_ids, params, threads)


if __name__ == "__main__":
    app()
