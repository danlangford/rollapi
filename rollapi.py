# coding=utf-8
import dice
from flask import Flask
from flask import jsonify
from flask import request
import requests
import os
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'api around python "dice" lib thrown together by @danlangford'


@app.route('/api/v1/roll/<roll_cmd>')
def get_roll(roll_cmd):
    return str(_get_roll(roll_cmd))


def _get_roll(roll_cmd):
    return dice.roll(roll_cmd)


@app.route('/api/v1/msteams', methods=['POST'])
def msteams():
    body = request.get_json()
    if body['type'] != 'message':
        nomsg = "we do not yet handle type " + body['type']
        app.logger.info(nomsg)
        return nomsg
    serviceUrl = body['serviceUrl']


    text = body['text']
    app.logger.info("text="+text)
    if "<at>DiceBot</at>" in text:
        text = text.partition("<at>DiceBot</at>")[2]
    slash_command = text.partition("roll")[2].strip()
    app.logger.info("slash_command="+slash_command)

    roll_msg, other_msg, color = _msteams(slash_command)

    _convo = body['conversation']
    _id = body['id']

    message='{} {}'.format(roll_msg, other_msg)

    app.logger.info("message="+message)


    outpayload = {'type': 'message',
                    'from': body['recipient'],
                    'conversation': _convo,
                    'recipient':body['from'],
                    'replyToId':_id,
                    'text':message}

    requests.post(body['serviceUrl']+'v3/conversations/'+_convo['id']+'/activities/'+_id,
                  json=outpayload,
                  headers={'Authorization':'Bearer '+_msteams_access_token()} )

    return jsonify(outpayload)


def _msteams_access_token():
    msAppId=os.environ['MICROSOFT-APP-ID']
    msAppPw=os.environ['MICROSOFT-APP-PASSWORD']
    tokenRes = requests.post('https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token',
                  data={'grant_type':'client_credentials',
                        'client_id':msAppId,
                        'client_secret':msAppPw,
                        'scope':'https://api.botframework.com/.default'})
    return json.loads(tokenRes.text)['access_token']


def _msteams(slash_command):
    # TODO: this method is still hipchat, fix
    color = 'yellow'
    other_msg = ''
    try:
        # isolates the roll syntax from any other message
        roll_syntax, _d, other_msg = slash_command.partition(' ')

        if roll_syntax.lower().strip() in ['help', '']:
            color = 'gray'
            roll = 'try things like d6 2d8 1d20+3 4d6^3 2d20v1 5d6s 4d10t'
            other_msg = 'where s=sort t=total ^=top_values v=bottom_values'
        else:
            roll = _get_roll(roll_syntax)
    except Exception as e:
        app.logger.error(e)
        color = 'red'
        roll = 'Exception: {}'.format(e)

    if isinstance(roll, (list, tuple)) and not isinstance(roll, basestring):
        if len(roll) == 1:
            roll_msg = str(roll[0])
        else:
            roll_msg = '{} (Σ={})'.format(roll, sum(roll))
    else:
        roll_msg = str(roll)

    return roll_msg, other_msg, color


@app.route('/api/v1/hipchat', methods=['POST'])
def hipchat():
    body = request.get_json()
    from_name = body['item']['message']['from']['mention_name']
    slash_command = body['item']['message']['message'].strip()
    roll_msg, other_msg, color = _hipchat(slash_command)
    message = '@{} {} {}'.format(from_name, roll_msg, other_msg)
    return jsonify({'color': color, 'message': message, 'notify': False,
                    'message_format': 'text'})


def _hipchat(slash_command):
    color = 'yellow'
    other_msg = ''
    try:
        # 1st partition() removes the command (/roll)
        # 2nd partition() isolates the roll syntax from any other message
        roll_syntax, _d, other_msg = slash_command.partition(' ')[2].partition(' ')

        if roll_syntax.lower().strip() in ['help', '']:
            color = 'gray'
            roll = 'try things like d6 2d8 1d20+3 4d6^3 2d20v1 5d6s 4d10t'
            other_msg = 'where s=sort t=total ^=top_values v=bottom_values'
        else:
            roll = _get_roll(roll_syntax)
    except Exception as e:
        app.logger.error(e)
        color = 'red'
        roll = 'Exception: {}'.format(e)

    if isinstance(roll, (list, tuple)) and not isinstance(roll, basestring):
        if len(roll) == 1:
            roll_msg = str(roll[0])
        else:
            roll_msg = '{} (Σ={})'.format(roll, sum(roll))
    else:
        roll_msg = str(roll)

    return roll_msg, other_msg, color


if __name__ == '__main__':
    app.run()
