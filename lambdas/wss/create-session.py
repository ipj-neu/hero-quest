import string, secrets, logging
from botocore.exceptions import ClientError
from boto3 import resource
from util import log_error, post_to_connection

def handler(event, context):
    try:
        cxt = event.get("requestContext", {})
        con_id = cxt.get("connectionId")
        domain = cxt.get("domainName")
        code_vals = string.ascii_uppercase + string.digits
        code = "".join(secrets.choice(code_vals) for _ in range(5))
        session = {
            "sessionCode": code,
            "dm": con_id,
        }
        try:
            resource("dynamodb").Table("sessions-v1").put_item(Item=session)
        except ClientError as e:
            log_error(e) 
            return {"statusCode": 500}
        post_to_connection({"sessionCode": code}, con_id, code, domain)
        return {"statusCode": 201}
    except Exception as e:
        log_error(e)
        return {"statusCode": 500}