import json
import dice
#import requests
import logging
from bs4 import BeautifulSoup


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
  """
    Parameters
    ----------
    event: dict, required
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
  """

  path = event["path"]
  logger.info(f"path={path}")
  if path.startswith("/api/v1/roll"):
    if len(event["pathParameters"]["roll_cmd"]) > 0:
      roll_cmd = event["pathParameters"]["roll_cmd"]
      logger.info(f"roll_cmd={roll_cmd}")
      resp = get_roll(roll_cmd)
    else:
      resp = "syntax=/api/v1/roll/{dice} " \
           "try dice like d6 2d8 1d20+3 4d6^3 2d20v1 5d6s 4d10t " \
           "where s=sort t=total ^=top_values v=bottom_values"
  elif path == "/api/v1/msteams":
    resp = msteams(json.loads(event["body"]))
  elif path == "/api/v1/hipchat":
    resp = hipchat(json.loads(event["body"]))
  else:
    resp = "api around python 'dice' lib thrown together by @danlangford. try GETting `./api/v1/roll/3d6`"

  return {"statusCode": 200, "body": json.dumps(resp)}


def get_roll(roll_cmd):
  roll = dice.roll(roll_cmd)
  if isinstance(roll, (list, tuple)) and not isinstance(roll, (str, bytes)):
    if len(roll) == 1:
      roll_msg = str(roll[0])
    else:
      roll_msg = "{} (Σ={})".format(roll, sum(roll))
  else:
    roll_msg = str(roll)
  return roll_msg


def msteams(body):
  if body["type"] != "message":
    nomsg = "we do not yet handle type " + body["type"]
    logger.info(nomsg)
    return nomsg

  html = body["text"]
  logger.info("html=" + html)
  html = html.replace("<at>RollDice</at>","")
  soup = BeautifulSoup(html, features="html.parser")
  text = soup.get_text().strip()
  logger.info("text=" + text)

  roll_msg, other_msg, color = _msteams(text)

  _convo = body["conversation"]
  _id = body["id"]

  message = "{} {}".format(roll_msg, other_msg)

  logger.info("message=" + message)

  outpayload = {
      "type": "message",
      "from": body["recipient"],
      "conversation": _convo,
      "recipient": body["from"],
      "replyToId": _id,
      "text": message,
  }

  # requests.post(
  #     body["serviceUrl"] + "v3/conversations/" + _convo["id"] + "/activities/" +
  #     _id,
  #     json=outpayload,
  #     headers={"Authorization": "Bearer " + _msteams_access_token()},
  # )

  return outpayload


# def _msteams_access_token():
#   msAppId = os.environ["MICROSOFT_APP_ID"]
#   msAppPw = os.environ["MICROSOFT_APP_PASSWORD"]
#   tokenRes = requests.post(
#       "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token",
#       data={
#           "grant_type": "client_credentials",
#           "client_id": msAppId,
#           "client_secret": msAppPw,
#           "scope": "https://api.botframework.com/.default",
#       },
#   )
#   return json.loads(tokenRes.text)["access_token"]


def _msteams(slash_command):
  # TODO: this method is still hipchat, fix
  color = "yellow"
  other_msg = ""
  try:
    # isolates the roll syntax from any other message
    roll_syntax, _d, other_msg = slash_command.partition(" ")

    if roll_syntax.lower().strip() in ["help", ""]:
      color = "gray"
      roll_msg = "try things like d6 2d8 1d20+3 4d6^3 2d20v1 5d6s 4d10t"
      other_msg = "where s=sort t=total ^=top_values v=bottom_values"
    else:
      roll_msg = get_roll(roll_syntax)
  except Exception as e:
    logger.error(e)
    color = "red"
    roll_msg = "Exception: {}".format(e)

  return roll_msg, other_msg, color


def hipchat(body):
  from_name = body["item"]["message"]["from"]["mention_name"]
  slash_command = body["item"]["message"]["message"].strip()
  roll_msg, other_msg, color = _hipchat(slash_command)
  message = "@{} {} {}".format(from_name, roll_msg, other_msg)
  return {
      "color": color,
      "message": message,
      "notify": False,
      "message_format": "text"
  }


def _hipchat(slash_command):
  color = "yellow"
  other_msg = ""
  try:
    # 1st partition() removes the command (/roll)
    # 2nd partition() isolates the roll syntax from any other message
    roll_syntax, _d, other_msg = slash_command.partition(" ")[2].partition(" ")

    if roll_syntax.lower().strip() in ["help", ""]:
      color = "gray"
      roll_msg = "try things like d6 2d8 1d20+3 4d6^3 2d20v1 5d6s 4d10t"
      other_msg = "where s=sort t=total ^=top_values v=bottom_values"
    else:
      roll_msg = get_roll(roll_syntax)
  except Exception as e:
    logger.error(e)
    color = "red"
    roll_msg = "Exception: {}".format(e)

  return roll_msg, other_msg, color
