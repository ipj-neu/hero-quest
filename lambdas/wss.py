import json, logging, boto3, string, secrets
from botocore.exceptions import ClientError
import util

# TODO i fucking did it. i can finally refactor this fucking garbage into fucking layer. 4 fucking hours. just to need to add a folder. just fuck. i am so dumb

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_error(e):
    logger.exception(getattr(e, "message", repr(e)))

class WssDm():
    def __init__(self, event, body):
        self.body = body

        self.session_code = body.get("sessionCode", None)

        self.cxt = event.get("requestContext", {})
        self.con_id:str = self.cxt.get("connectionId")

        self.session_tbl = boto3.resource("dynamodb").Table("sessions-v1")
        
    # HELPERS
    def create_client(self):
        return boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{self.cxt.get('domainName', '')}/v1")

    def post_to_connection(self, data, con_id):
        data = json.dumps(data).encode("utf-8")
        client = self.create_client()
        try:
            client.post_to_connection(Data=data, ConnectionId=con_id)
        except client.exceptions.GoneException:
            self.session_tbl.update_item(
                Key={ "sessionCode": self.session_id },
                UpdateExpression="DELETE players :con_id",
                ExpressionAttributeValues={ ":con_id": set([con_id])}
            )
            
    def get_session(self):
        if self.session_code == None: return False, None
        try:
            # TODO change key to dict
            session = self.session_tbl.get_item(Key={"sessionCode": self.session_code}).get("Item", None)
            if session == None: return False, None
            return True, session
        except ClientError as e:
            log_error(e)
            return False, None
            
    # WSS ACTIONS
    def create_session(self):
        try:
            code_vals = string.ascii_uppercase + string.digits
            session = {
                "sessionCode": "".join(secrets.choice(code_vals) for _ in range(5)),
                "dm": self.con_id,
            }
            self.session_tbl.put_item(Item=session)
            return 201
        except ClientError as e:
            log_error(e)
            return 500
    
    def join_session(self):
        valid, _ = self.get_session()
        if not valid: return 404
        try:
            self.session_tbl.update_item(
                Key={"sessionCode": self.session_code},
                UpdateExpression="ADD players :con_id",
                ExpressionAttributeValues={":con_id": set([self.con_id])}
            )
            return 200
        except ClientError as e:
            log_error(e)
            return 500
    
    def update_dm(self):
        valid, session = self.get_session()
        hero = self.body.get("hero", None)
        if not valid or hero == None: return 404
        self.post_to_connection(hero, session.get("dm"))
        return 200

# TODO add checks to make sure that all the endpoint that send a response can get a session_id in the body
def main(event, context):
    route_key = event.get("requestContext", {}).get("routeKey")
    body:dict = json.loads(event.get("body", {}))
    handler = WssDm(event, body)

    response = {"statusCode": 400}
    
    if route_key == "createSession":
        response["statusCode"] = handler.create_session()
    elif route_key == "joinSession":
        response["statusCode"] = handler.join_session()
    elif route_key == "updateDm":
        response["statusCode"] = handler.update_dm()
        
    return response

if __name__ == "__main__":
    main({}, {})