import boto3, json, logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_error(e):
    logger.exception(getattr(e, "message", repr(e)))

def create_client(domain):
    return boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{domain}/v1")

def post_to_connection(data, con_id, session_code, domain, session_tbl=boto3.resource("dynamodb").Table("session-v1")):
    data = json.dumps(data).encode("utf-8")
    client = create_client(domain)
    try:
        client.post_to_connection(Data=data, ConnectionId=con_id)
    except client.exceptions.GoneException:
        session_tbl.update_item(
            Key={ "sessionCode": session_code },
            UpdateExpression="DELETE players :con_id",
            ExpressionAttributeValues={ ":con_id": set([con_id])}
        )

def get_session(session_code, session_tbl=boto3.resource("dynamodb").Table("session-v1")):
    if session_code == None: return False, None
    try:
        session = session_tbl.get_item(Key={"sessionCode": session_code}).get("Item", None)
        if session == None: return False, None
        return True, session
    except ClientError as e:
        log_error(e)
        return False, None