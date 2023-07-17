from util import post_to_connection, get_session
from boto3 import resource
from json import loads

def handler(event, context):
    body = loads(event.get("body", {}))
    session_tbl = resource("dynamodb").Table("sessions-v1")
    session_code = body.get("sessionCode", None)

    valid, session = get_session(session_code, session_tbl)
    hero = body.get("hero", None)
    if not valid or hero == None: return {"statusCode": 404}
    post_to_connection(hero, session.get("dm"), session_code, event.get("requestContext", {}).get("domainName", ""), session_tbl)
    return {"statusCode": 200}