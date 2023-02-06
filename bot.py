import configparser
import os
from mastodon import Mastodon
import random
import string
import base64

def encrypt(text, method, key):
    if method == "A1Z26":
        result = ""
        for char in text:
            if char.isalpha():
                if char.isupper():
                    result += str(ord(char) - 65 + 1) + ' '
                else:
                    result += str(ord(char) - 97 + 1) + ' '
            else:
                result += char
        return result

    elif method == "ATBASH":
        result = ""
        for char in text:
            if char.isalpha():
                if char.isupper():
                    result += chr(90 - (ord(char) - 65))
                else:
                    result += chr(122 - (ord(char) - 97))
            else:
                result += char
        return result

    elif method == "Caesar":
        result = ""
        key = int(key)
        for char in text:
            if char.isalpha():
                if char.isupper():
                    result += chr((ord(char) - 65 + key) % 26 + 65)
                else:
                    result += chr((ord(char) - 97 + key) % 26 + 97)
            else:
                result += char
        return result
    
    elif method == "Vigenère":
        result = ""
        i = 0
        for char in text:
            if char.isalpha():
                if char.isupper():
                    result += chr((ord(char) - 65 + ord(key[i % len(key)].upper()) - 65) % 26 + 65)
                else:
                    result += chr((ord(char) - 97 + ord(key[i % len(key)].upper()) - 65) % 26 + 97)
                i += 1
            else:
                result += char
        return result
    
    elif method == "Rail Fence":
        rails = [[] for i in range(key)]
        rail_index, direction = 0, 1
        for char in text:
            rails[rail_index].append(char)
            if rail_index + direction == key - 1 or rail_index + direction == 0:
                direction *= -1
            rail_index += direction
        return ''.join([''.join(rail) for rail in rails])
        
    elif method == "Playfair":
        result = ""
        key = str(key.upper())
        key_matrix = create_key_matrix(key)
        text = text.upper()
        text = text.replace("J", "I")
        text = [text[i:i+2] for i in range(0, len(text), 2)]
        for pair in text:
            if len(pair) == 1:
                pair += "X"
            pos1 = [(i, key_matrix[i].index(pair[0])) for i in range(5) if pair[0] in key_matrix[i]][0]
            pos2 = [(i, key_matrix[i].index(pair[1])) for i in range(5) if pair[1] in key_matrix[i]][0]
            if pos1[0] == pos2[0]:
                result += key_matrix[pos1[0]][(pos1[1]+1)%5] + key_matrix[pos2[0]][(pos2[1]+1)%5]
            elif pos1[1] == pos2[1]:
                result += key_matrix[(pos1[0]+1)%5][pos1[1]] + key_matrix[(pos2[0]+1)%5][pos2[1]]
            else:
                result += key_matrix[pos1[0]][pos2[1]] + key_matrix[pos2[0]][pos1[1]]
        return result
    
    elif method == "Base64":
        return base64.b64encode(text.encode()).decode()
        
    else:
        return text

def create_key_matrix(key):
    key = key.upper().replace("J", "I")
    matrix = []
    for char in key:
        if char not in matrix:
            matrix.append(char)
    for i in range(65, 91):
        char = chr(i)
        if char not in matrix and char != "J":
            matrix.append(char)
    return [matrix[i:i+5] for i in range(0, 25, 5)]


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(rf'{ROOT_DIR}\config.ini'):
    url = input("Enter the URL of your Mastodon instance:\n")
    email = input("Enter your email address:\n")
    password = input("Enter your password:\n")
    
    app_info = Mastodon.create_app(
        "Encoder",
        api_base_url = f"{url}"
    )
    client_id, client_secret = app_info

    mastodon = Mastodon(client_id=client_id, client_secret=client_secret, api_base_url=url)
    access_token = mastodon.log_in(email, password)

    config = configparser.ConfigParser()
    config['MASTODON'] = {'url': url,
                          'email': email,
                          'password': password,
                          'client_id': client_id,
                          'client_secret': client_secret,
                          'access_token': access_token}
    
    with open(rf'{ROOT_DIR}\config.ini', 'w') as configfile:
        config.write(configfile)

config = configparser.ConfigParser()
config.read(rf'{ROOT_DIR}\config.ini')
url = config['MASTODON']['url']
email = config['MASTODON']['email']
password = config['MASTODON']['password']
client_id_str = config['MASTODON']['client_id']
client_secret_str = config['MASTODON']['client_secret']
access_token_str = config['MASTODON']['access_token']

mastodon = Mastodon(client_id=client_id_str, client_secret=client_secret_str, access_token=access_token_str, api_base_url=url)

while True:
    post_text = input("Please input your text for the post\n")
    
    if post_text == "":
        continue
    else:
        pass
    
    spoiler = input("If you would like a content warning, please type it below. If not, leave it blank\n")
    
    if spoiler == "":
        pass
    else:
        pass
    
    break

methods = ["A1Z26", "ATBASH", "Caesar", "Vigenère", "Rail Fence", "Playfair"]
method_choice = random.choice(methods)
key_choice = random.choices(string.ascii_lowercase, k = 1024)

encode_text = encrypt(text = post_text, method = method_choice, key = key_choice)

try:
    post = mastodon.status_post(status = encode_text,
                                spoiler_text = spoiler)
except Exception as e:
    print(f"Exception: {e}")

post_id = post["id"]
post_content = post["content"]

print(f"Posted!\nCipher used: {method_choice}\nStatus ID = {post_id}\nStatus content (HTML code):\n{post_content}")