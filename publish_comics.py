import requests
import os
import random
from dotenv import load_dotenv
from urllib.parse import urlparse
import telegram


def fetch_comics_info(num=1) -> requests.Response:
    link_template = f"https://xkcd.com/{num}/info.0.json"
    response = requests.get(link_template, timeout=20)
    response.raise_for_status()
    return response.json()


def get_img_format(link: str) -> str:
    parsed_url = urlparse(link)
    if not parsed_url.scheme:
        link = f"http://{link}"
        parsed_url = urlparse(link)
    return parsed_url.path.split(".")[-1]


def save_comics_image(
    link, folder_name: str = "comics", img_title: str = "img_title"
) -> str:
    os.makedirs(folder_name, exist_ok=True)
    img_format = get_img_format(link)
    img_name = f"{img_title}.{img_format}"
    img_path = os.path.join(folder_name, img_name)
    with open(img_path, "wb") as image:
        response = requests.get(link, timeout=20)
        response.raise_for_status()
        image.write(response.content)
    return img_path


def get_current_comics_info() -> requests.Response:
    response = requests.get("https://xkcd.com/info.0.json", timeout=20)
    response.raise_for_status()
    return response.json()


def save_random_comics(folder_name: str = "comics") -> tuple[str, str]:
    current_comics_num = int(get_current_comics_info()["num"])
    random_num = random.randint(1, current_comics_num)
    comics_info = fetch_comics_info(random_num)
    comics_alt = comics_info["alt"]
    img_link = comics_info["img"]
    img_safe_title = comics_info["safe_title"]
    comics_path = save_comics_image(img_link, folder_name, img_safe_title)
    return comics_path, comics_alt


def main():
    load_dotenv(".env")
    bot_token = os.environ["TG_BOT_TOKEN"]
    group_id = os.environ["TG_GROUP_ID"]
    bot = telegram.Bot(bot_token)
    path, alt = save_random_comics()
    with open(path, "rb") as photo:
        bot.send_photo(chat_id=group_id, photo=photo, caption=alt)
    os.remove(path)


if __name__ == "__main__":
    main()
