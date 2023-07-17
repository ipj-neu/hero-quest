from util import get_session, log_error
from botocore.exceptions import ClientError
from json import loads
from boto3 import resource

def handler(event, context):
    con_id = event.get("requestContext", {}).get("connectionId")
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
        return {"statusCode": 200}
    except ClientError as e:
        log_error(e)
        return 500