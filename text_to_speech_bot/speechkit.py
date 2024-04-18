from config import MAX_SYMBOLS_PER_REQUETS, MAX_SYMBOLS_PER_USER
from dotenv import get_key
import requests
import time
from conspiracy import iam_data
from db import get_user_chars, update_user_chars, add_user


folder_id = get_key('.env', 'FOLDER_ID')
users = {}


def create_new_iam_token() -> dict[str: str]:
    """Возвращает метадату нового IAM"""
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    return response.json()


def check_iam() -> None:
    """Проверяет истек ли срок годности IAM токена. Если истек, то вызывает create_new_iam_token()"""  # Тут кое-где
    # докстринги и тайп хинты есть, а кое-где нет потому что я занимаюсь копипастой из старого
    # проекта(ну свой же не считается...? ). А оформлять это все красиво времени нет.
    # Долго слишком прокрастинировал. Но в финальном все как положено будет
    global expires_at
    if expires_at < time.time():
        global iam
        iam_data = create_new_iam_token()
        iam = iam_data['access_token']
        expires_at = iam_data['expires_in']


#  token_data = create_new_iam_token()
token_data = iam_data
iam = token_data['access_token']
expires_at = time.time() + token_data['expires_in']


class Speechkit:
    """Класс, через который реализовано все взаимодействие пользователя со speechkit"""
    def __init__(
            self,
            user_id,
            chars=MAX_SYMBOLS_PER_USER,
            api_link='https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    ):
        self.user_id = user_id
        self.api = api_link
        self.chars = chars
        users[user_id] = self

    def text_to_speech(self, text):
        check_iam()
        if len(text) > MAX_SYMBOLS_PER_REQUETS:
            return 'exc', 'Слишком длинный текст для одного запроса. Попробуйте написать это покороче'
        if get_user_chars(self.user_id) < len(text):
            return 'exc', f'Текст слишком длинный. Вы можете преобразовать еще {len(text)} символов'
        else:
            headers = {'Authorization': f'Bearer {iam}'}
            data = {
                'text': text,
                'lang': 'ru-RU',
                'voice': 'alena',
                'speed': 1
            }
            req = requests.post(self.api, headers=headers, data=data)
            if req.status_code != 200:
                print(req.json())
                return 'err', f'Что-то поломалось. Код ошибки: {req.status_code}'
            else:
                self.chars -= len(text)
                update_user_chars(self.user_id, self.chars)
                return 'succ', req.content
