#/usr/bin/python3
from bs4 import BeautifulSoup
import typer
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import os


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
            # proxies=PROXIES,
            # verify=False,
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
        print(f"[+] {counter} pages crawled.")
    return source_ids


def print_clean_source_code(src, source_id, s2f):
    soup = BeautifulSoup(src, 'html.parser')
    pre_tags = soup.find_all('pre')
    # Combine all text from <pre> tags
    full_source_code = "\n".join(pre.get_text() for pre in pre_tags)
    if s2f == False:
        print(full_source_code)
    else:
        folder_name = "output"
        os.makedirs(folder_name, exist_ok=True)
        
        # Save the source code to a file named after source_id inside the folder
        file_path = os.path.join(folder_name, f"{source_id.replace('/','-').replace('\\','')}.txt")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(full_source_code)
        print(f"[+] {source_id} Source code saved to {file_path}")
        

def get_source_code(source_id, params, s2f):
    params['id'] = source_id
    r = requests.get(
        'https://grep.app/api/file',
        params=params,
        # proxies=PROXIES,
        # verify=False,
    )
    if r.status_code != 200:
        print(f"Error fetching source code for ID {source_id}.")
        return
    print_clean_source_code(r.text, source_id, s2f)


def fetch_all_source_codes_concurrently(source_ids, params, threads, s2f):
    with ThreadPoolExecutor(max_workers=threads) as executor:  # Adjust `max_workers` as needed
        futures = [executor.submit(get_source_code, source_id, params, s2f) for source_id in source_ids]
        for future in futures:
            future.result()  # Wait for all threads to complete


app = typer.Typer()

@app.command()
def search(search: str, regex: bool = False, regexp: bool = False, lang: str = "", threads: int = 10, s2f: bool = False):
    """Just a simple tool to extract source codes from grep.app"""
    params = {'q': search}
    if regexp:
        params['regexp'] = regexp
    if lang:
        params['f.lang'] = lang
    
    source_ids = get_all_source_code_ids(params)
    fetch_all_source_codes_concurrently(source_ids, params, threads, s2f)


if __name__ == "__main__":
    app()
