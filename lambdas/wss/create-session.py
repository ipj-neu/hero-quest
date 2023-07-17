import string, secrets, logging
from botocore.exceptions import ClientError
from boto3 import resource

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    con_id = event.get("requestContext", {}).get("connectionId")
    try:
        code_vals = string.ascii_uppercase + string.digits
        session = {
            "sessionCode": "".join(secrets.choice(code_vals) for _ in range(5)),
            "dm": con_id,
        }
        resource("dynamodb").Table("sessions-v1").put_item(Item=session)
        return {"statusCode": 201}
    except ClientError as e:
        logger.exception(getattr(e, "message", repr(e)))
        return 500