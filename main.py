import json
import logging
import os

from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

sp = ["слона", "кролика"]


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {sp[0]}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        "я покупаю",
        'я куплю'
    ]:
        if len(sp) >= 2:
            res['response'][
                'text'] = f'{sp[0].capitalize()} можно найти на Яндекс.Маркете! А теперь купи {sp[1]}'
            del sp[0]
            return
        else:
            res['response'][
                'text'] = f'{sp[0].capitalize()} можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True
            return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {sp[0]}!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
