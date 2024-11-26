from bs4 import BeautifulSoup
import typer
import requests
import json

PROXIES = {
    "http": "http://127.0.0.1:8080",  # Burpsuite proxy
    "https": "http://127.0.0.1:8080",
}


# functions
def getAllSourceCodeIds(params):
    source_ids = []
    prev_resp = ""
    counter = 1
    while True:
        src_list = requests.get('https://grep.app/api/search?page='+str(counter),params=params
                                ,proxies=PROXIES, verify=False
                                )
        if src_list.status_code != 200:
            exit("something went wrong!")
        if prev_resp == src_list.text[:-27]:
            break
        prev_resp = src_list.text[:-27]
        counter += 1
        json_data = json.loads(src_list.text)
        # print(json_data['hits']['hits'])
        for src in json_data['hits']['hits']:
            source_ids.append(src['id']['raw'])
    return source_ids

def printCleanSourceCode(src):
        soup = BeautifulSoup(src, 'html.parser')
        pre_tags = soup.find_all('pre')
        for pre in pre_tags:
            print(pre.get_text())



def getSourceCode(source_id, params):
    params['id'] = source_id
    r = requests.get('https://grep.app/api/file', params=params
                                ,proxies=PROXIES, verify=False
                                )
    if r.status_code != 200:
        exit("something went wrong!")
    printCleanSourceCode(r.text)



app = typer.Typer()

@app.command()
def search(search: str, regex: bool = False, regexp: bool = False, lang: str = ""):
    """just a simple tool to extract source codes from grep.app"""
    params = {'q': search}
    if regexp != False:
        params['regexp'] = regexp
    if lang != "":
        params['f.lang'] = lang
    
    source_ids = getAllSourceCodeIds(params)
    for source_id in source_ids:
        getSourceCode(source_id, params)
    


if __name__ == "__main__":
    app()
