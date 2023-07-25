from util import get_session, log_error, post_to_connection
from botocore.exceptions import ClientError
from json import loads
from boto3 import resource

def handler(event, context):
    try:
        cxt = event.get("requestContext", {})
        con_id = cxt.get("connectionId")
        domain = cxt.get("domainName")
        session_tbl = resource("dynamodb").Table("sessions-v1")
        session_code = loads(event.get("body", {})).get("sessionCode", None)

        valid, _ = get_session(session_code, session_tbl)
        if not valid: return {"statusCode": 404}
        try:
            session_tbl.update_item(
                Key={"sessionCode": session_code},
                UpdateExpression="ADD players :con_id",
                ExpressionAttributeValues={":con_id": set([con_id])}
            )
        except ClientError as e:
            log_error(e)
            return {"statusCode": 500}

        post_to_connection({"action": "successfulJoin", "session_code": session_code}, con_id, session_code, domain, session_tbl)
        return {"statusCode": 200}
    except:
        log_error(e)
        return {"statusCode": 500}