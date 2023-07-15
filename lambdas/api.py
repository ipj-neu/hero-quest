import json, logging, boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# HELPERS
        
def send_error(code, msg):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({ "message": msg })
    } 

def send_data(code, data):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(data)
    }
        
def main(event, context):
    return send_data(200, {"msg": "pong"})