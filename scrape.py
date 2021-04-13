
import pandas as pd
from tqdm import tqdm


from request_handler import RequestHandler
from settings import URLS, BASE_URL


req_handler = RequestHandler()


def burl(u): return f"{BASE_URL}{u}"


def fetch_victim_urls(group_url):
    soup = req_handler.get_soup(burl(group_url))
    if not soup: return []
    url_tags = soup.find_all("a", class_="topiclink")
    url_tags = list(filter(lambda u: "," in u.get_text() , url_tags))
    urls = list(map(lambda u: u["href"], url_tags))
    return urls
    
def clean_text(text):
    text = " ".join(text.split())
    return text

def get_bio(soup):
    bio_table = soup.find_all("table")[2]
    text_snippets = bio_table.find_all("p", class_="p_Normal")
    text_full = " ".join(list(map(lambda sn: sn.get_text(), text_snippets)))
    return clean_text(text_full)
    
    
def get_legend(li, i):
    if (i+1) >= len(li):
        try:
            return clean_text(li[i].find_all("span", class_="f_Bildlegende")[0].get_text())
        except:            
            return li[i].find_all("img")[0]["alt"]
    return clean_text(li[i+1].get_text())
    
    
def get_images(soup):
    images = []
    # all_images = soup.find_all("img")
    all_images_and_legends = soup.find_all("p", class_="p_Bildlegende")
    for i, img in enumerate(all_images_and_legends):
        if img.find_all("img"):
            src = img.find_all("img")[0]["src"]
            images.append({
                "legende": get_legend(all_images_and_legends, i),
                "src": src,
            })
    return images
    
def extract_name(url):
    # https://www.stolpersteine-konstanz.de/adler_emma.html
    names = url.replace(BASE_URL, "")[:-5].split("_")
    if len(names) == 0:
        names = [""]
    if len(names) == 1:
        names.append("")
    if len(names) == 3:
        mid_name = names[1]
        first_name = names[2]
        names[1] = f"{first_name} {mid_name}" 
    return names        

def fetch_victim_data(url):
    soup = req_handler.get_soup(burl(url))
    if not soup: return False
    images = get_images(soup)
    bio = get_bio(soup)
    name = extract_name(url)    
    return {
        "vorname": name[1], 
        "nachname": name[0],
        "bio": bio,
        "images": images,
        "url": burl(url),
    }


def fetch_victims():
    print("> Fetching victims <")
    victims = []
    victim_urls = []
    for key in URLS.keys():
        print(f"> Getting names and urls for group '{key}'")
        group_url = URLS[key]
        victim_urls += fetch_victim_urls(group_url)
    print(f"{50*'-'}\n> Downloading victim data <")
    for v_url in tqdm(victim_urls):
        victims.append(fetch_victim_data(v_url))
    
    df = pd.DataFrame(victims)
    df = df[df['bio'].ne('bio') & df['vorname'].ne('vorname') & df['nachname'].ne('nachname')]
    df["id"] = df.index
    df_2 = df["images"].apply(pd.Series)
    df_2["id"] = df.index
    df = pd.merge(df, df_2, on = "id", how = "inner")
    return df



df = fetch_victims()
print(df)

df.to_csv("victim_data.csv", index=False, encoding="utf-8")
