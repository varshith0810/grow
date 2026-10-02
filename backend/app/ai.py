import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from .settings import settings
class BedrockPredictor:
    def __init__(self): self.client=boto3.client("bedrock-runtime",region_name=settings.aws_region)
    def predict(self,symbol:str,timeframe:str):
        prompt=f"""You are a market-analysis assistant.
Stock: {symbol}
Timeframe: {timeframe}
Return ONLY valid JSON with signal (GREEN, RED, or NEUTRAL), confidence from 0 to 1, rationale (array of strings), and risk.
Do not claim certainty or provide personalized financial advice."""
        try:
            response=self.client.converse(modelId=settings.bedrock_model_id,messages=[{"role":"user","content":[{"text":prompt}]}],inferenceConfig={"maxTokens":500,"temperature":0.1})
            data=json.loads(response["output"]["message"]["content"][0]["text"].strip())
            signal=data.get("signal","NEUTRAL")
            if signal not in {"GREEN","RED","NEUTRAL"}: signal="NEUTRAL"
            return {"symbol":symbol,"timeframe":timeframe,"signal":signal,"confidence":max(0,min(1,float(data.get("confidence",0)))),"rationale":data.get("rationale",[]),"risk":data.get("risk","Unknown")}
        except (BotoCoreError,ClientError,ValueError,KeyError,json.JSONDecodeError):
            return {"symbol":symbol,"timeframe":timeframe,"signal":"NEUTRAL","confidence":0,"rationale":["AI prediction is temporarily unavailable."],"risk":"Unavailable"}
