import requests
import os
import random
from dotenv import load_dotenv
from urllib.parse import urlparse
import telegram


def fetch_comics_info(num: int = 1) -> requests.Response:
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
    img_format = get_img_format(link)
    img_name = f"{img_title}.{img_format}"
    img_path = os.path.join(folder_name, img_name)
    response = requests.get(link, timeout=20)
    response.raise_for_status()
    with open(img_path, "wb") as image:
        image.write(response.content)
    return img_path


def get_rnd_comics_num() -> int:
    response = requests.get("https://xkcd.com/info.0.json", timeout=20)
    response.raise_for_status()
    current_comics_num = int(response.json()["num"])
    return random.randint(1, current_comics_num)


def main():
    load_dotenv(".env")
    bot_token = os.environ["TG_BOT_TOKEN"]
    group_id = os.environ["TG_GROUP_ID"]
    folder_name = os.getenv("FOLDER")
    if not folder_name:
        folder_name = "comics"
    os.makedirs(folder_name, exist_ok=True)
    bot = telegram.Bot(bot_token)
    try:
        rnd_comics_num = get_rnd_comics_num()
        rnd_comics_info = fetch_comics_info(rnd_comics_num)
        alt = rnd_comics_info["alt"]
        img_link = rnd_comics_info["img"]
        safe_title = rnd_comics_info["safe_title"]
        img_path = save_comics_image(img_link, folder_name, safe_title)
        with open(img_path, "rb") as photo:
            bot.send_photo(chat_id=group_id, photo=photo, caption=alt)
    finally:
        os.remove(img_path)


if __name__ == "__main__":
    main()
