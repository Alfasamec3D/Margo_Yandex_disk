
import requests
import urllib.parse
import os

folders=['ПОРТРЕТЫ','СТУДИЯ','УЛИЦА']
folder_map={
    'портрет:': 0,
    'фотографии со студии:': 1,
    'студия:': 1,
    'фотографии с улицы:': 2,
    'улица:': 2,
}

def get_unique_dir_name(base_path):
    '''
    Returns a directory path that does not exist yet.
    If 'base_path' exists, appends (2), (3), etc.
    '''

    path = base_path
    counter=2
    while os.path.exists(path):
        path=f"{base_path} ({counter})"
        counter+=1
    return path

def download_file(yandex_link, file_path, save_path):
    encoded_public_key=urllib.parse.quote(yandex_link, safe='')
    encoded_file_path=urllib.parse.quote(file_path, safe='')

    api_url=f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={encoded_public_key}&path={encoded_file_path}"

    response = requests.get(api_url)
    
    response.raise_for_status()
    download_info = response.json()

    download_url = download_info['href']
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


print("Приветствую! \nЭто программа автоматизированной загрузки фотографий с Яндекс диска.\n")

while True:
    pathto_txt=input("Введи путь к файлу .txt расширения со списком имён фотографий: ")

    try:
        with open(pathto_txt, "r", encoding="utf-8") as file:
            text = file.read()
        break
    except FileNotFoundError:
        print("❌ Файл не найден. Проверь путь и попробуй ещё раз.")
    except OSError as e:
        print(f"❌ Путь недействительный или файл нельзя открыть: {e}")


user_yandex_link=input("Введи ссылку на Яндекс диск: ")
api_url=f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={urllib.parse.quote(user_yandex_link, safe='')}"
response = requests.get(api_url)
response.raise_for_status()

disk_data=response.json()
print("Ответ от диска \"",disk_data["name"], "\" получен.\n")

user_save_path=input("Введи путь к папке для загрузки: ")

lines=text.splitlines()
current_section=None

fin_path=get_unique_dir_name(f"{user_save_path}/{disk_data['name']}")


for line in lines:
    line=line.strip()
    if not line:
        continue
    if line.lower() in folder_map:
        current_section=folder_map[line]
        continue
    
    if current_section is None:
    
        continue
    try:
        download_file(user_yandex_link, f"/{folders[current_section]}/{line.lower()}",f"{fin_path}/{folders[current_section]}/{line.lower()}")
    except requests.exceptions.HTTPError as http_err2:
        if (current_section==0) or (current_section==1):
            try:
                download_file(user_yandex_link, f"/{folders[(current_section+1)%2]}/{line.lower()}",f"{fin_path}/{folders[current_section]}/{line.lower()}")
            except requests.exceptions.HTTPError as http_err:
                #print(f"HTTP error occurred: {http_err}")
                print(f"/{folders[(current_section+1)%2]}/{line.lower()}\n")
        elif current_section==2:
            #print(f"HTTP error occurred: {http_err2}")
            print(f"/{folders[current_section]}/{line.lower()}\n")
print("Я заакончил")