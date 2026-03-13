import os
import json
import logging
import azure.functions as func
from azure.cosmos import CosmosClient
from openai import OpenAI

app = func.FunctionApp()

@app.event_hub_message_trigger(
    arg_name="azeventhub", 
    event_hub_name="logs",
    connection="EventHubConnectionString"
)
def process_security_logs(azeventhub: func.EventHubEvent):
    logging.info('Trigger processing event: %s', azeventhub.get_body().decode('utf-8'))
    
    raw_body = azeventhub.get_body().decode('utf-8')
    
    try:
        log_data = json.loads(raw_body)
    except json.JSONDecodeError:
        logging.error("Failed to parse body as JSON.")
        return

    if log_data.get("severity") == "INFO":
        return
        
    logging.info(f"Processing suspicious log: {log_data.get('event')}")
    
    api_key = os.getenv("OpenAIApiKey")
    if not api_key or api_key == "<ENTER_YOUR_OPENAI_API_KEY_HERE>":
        logging.error("OpenAIApiKey not configured.")
        return

    client = OpenAI(api_key=api_key)
    
    system_prompt = """
    You are a Level 1 Cloud Security Analyst. 
    Review the following server log entry. If it indicates a clear security threat 
    (like a brute force attack, SQL injection, etc.), output a JSON response with the following format:
    { "is_threat": true, "threat_type": "...", "description": "...", "recommended_action": "..." }
    
    If it is just a routine error or non-threatening spike, output:
    { "is_threat": false }
    
    Respond ONLY with valid JSON.
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(log_data)}
            ],
            response_format={ "type": "json_object" }
        )
        
        ai_response = json.loads(completion.choices[0].message.content)
        
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return

    if ai_response.get("is_threat"):
        logging.warning(f"Detected Threat: {ai_response.get('description')}")
        store_alert_in_cosmos(ai_response, log_data)
    else:
        logging.info("Not a threat.")

def store_alert_in_cosmos(ai_analysis, original_log):
    cosmos_conn_str = os.getenv("CosmosDbConnectionString")
    db_name = "securitylogs"
    container_name = "alerts"
    
    if not cosmos_conn_str or cosmos_conn_str == "<ENTER_YOUR_COSMOS_DB_CONNECTION_STRING_HERE>":
         logging.error("CosmosDbConnectionString missing.")
         return

    try:
        client = CosmosClient.from_connection_string(cosmos_conn_str)
        database = client.get_database_client(db_name)
        container = database.get_container_client(container_name)
        
        alert_document = {
            "id": f"{original_log.get('server')}-{original_log.get('process_id')}",
            "timestamp": original_log.get("timestamp"),
            "server": original_log.get("server"),
            "ip": original_log.get("ip"),
            "original_event": original_log.get("event"),
            "ai_threat_type": ai_analysis.get("threat_type"),
            "ai_description": ai_analysis.get("description"),
            "ai_recommended_action": ai_analysis.get("recommended_action")
        }
        
        container.create_item(body=alert_document)
        logging.info("Alert written to Cosmos DB.")
        
    except Exception as e:
         logging.error(f"Cosmos DB Error: {str(e)}")
