"""Direct-provider adapters for Experiment 3. Network use is explicit and entitlement-gated."""
from __future__ import annotations
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

class ProviderError(RuntimeError):
    def __init__(self,message:str,http_status:int|None=None,raw_body:bytes|None=None,error_type:str|None=None):
        super().__init__(message)
        self.http_status=http_status
        self.raw_body=raw_body
        self.error_type=error_type

def assert_free_only_entitlements(provider_config:dict)->None:
    """Fail closed unless all provider accounts are explicitly attested Free/no-overage."""
    policy=provider_config.get("defaults",{})
    if policy.get("api_spend_usd_max") != 0 or policy.get("paid_fallback") is not False:
        raise RuntimeError("zero-spend cap and disabled paid fallback are mandatory")
    if policy.get("prepaid_credits") is not False or policy.get("automatic_model_substitution") is not False:
        raise RuntimeError("prepaid credits and automatic model substitution must be disabled")
    if policy.get("external_tools") is not False:
        raise RuntimeError("external tools must be disabled for the zero-spend dry run")
    for code in ("A","B","C"):
        account=provider_config.get("provider_families",{}).get(code,{})
        if account.get("account_free_tier_verified") is not True:
            raise RuntimeError(f"provider {code} account Free entitlement is not verified")
        if account.get("billing_state") != "free_no_paid_overage":
            raise RuntimeError(f"provider {code} billing state is not verified as Free/no-overage")
        if account.get("quota_verified") is not True:
            raise RuntimeError(f"provider {code} quota is not verified")

def build_request(family:str,provider:dict,messages:list[dict],env:dict|None=None,temperature:float=0.0,max_output_tokens:int=2048)->Request:
    env=os.environ if env is None else env
    family={"G":"A","Z":"B","O":"C"}.get(family,family)
    model=provider["model"]
    if family=="A":
        key=env.get(provider.get("credential_env","GEMINI_API_KEY"))
        if not key: raise RuntimeError("Gemini API key environment variable is missing")
        url=provider["base_url"].rstrip("/")+"/models/"+quote(model,safe="")+":generateContent"
        system="\n\n".join(x["content"] for x in messages if x["role"]=="system")
        contents=[{"role":"user" if x["role"]=="user" else "model","parts":[{"text":x["content"]}]} for x in messages if x["role"]!="system"]
        body={"contents":contents,"generationConfig":{"temperature":temperature,"maxOutputTokens":max_output_tokens}}
        if system: body["systemInstruction"]={"parts":[{"text":system}]}
        headers={"Content-Type":"application/json","x-goog-api-key":key}
    elif family in {"B","C"}:
        key=env.get(provider.get("credential_env"))
        if not key: raise RuntimeError(f"{family} API key environment variable is missing")
        base=provider["base_url"].rstrip("/")
        if family=="B" and "${CLOUDFLARE_ACCOUNT_ID}" in base:
            account_id=env.get("CLOUDFLARE_ACCOUNT_ID")
            if not account_id: raise RuntimeError("CLOUDFLARE_ACCOUNT_ID environment variable is missing")
            base=base.replace("${CLOUDFLARE_ACCOUNT_ID}",account_id)
        url=base+"/chat/completions"
        body={"model":model,"messages":messages,"temperature":temperature,"max_tokens":max_output_tokens}
        headers={"Content-Type":"application/json","Authorization":"Bearer "+key}
    else:
        raise ValueError("family must be A, B or C")
    return Request(url,data=json.dumps(body,ensure_ascii=False,separators=(",",":")).encode("utf-8"),headers=headers,method="POST")

def dispatch(request:Request,timeout_seconds:int=60,opener=urlopen,raw_sink=None)->dict:
    """Perform exactly one HTTP attempt. Retry decisions belong to the harness layer."""
    try:
        with opener(request,timeout=timeout_seconds) as response:
            raw=response.read()
            status=getattr(response,"status",200)
            if raw_sink is not None: raw_sink(raw,status)
    except HTTPError as exc:
        raw=exc.read()
        if raw_sink is not None: raw_sink(raw,exc.code)
        raise ProviderError(f"provider returned HTTP {exc.code}",http_status=exc.code,raw_body=raw) from exc
    except (URLError,TimeoutError,ConnectionError) as exc:
        raise ProviderError(f"provider transport failure: {type(exc).__name__}",error_type="documented_transient_sdk_transport") from exc
    try:
        parsed=json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError,json.JSONDecodeError) as exc:
        raise ProviderError("provider returned a non-JSON transport envelope",http_status=status,raw_body=raw,error_type="invalid_transport_envelope") from exc
    return {"http_status":status,"raw_response_bytes":raw,"response_json":parsed}

def extract_text(family:str,response_json:dict)->dict:
    """Extract only explicit final text and provider metadata; never infer/repair."""
    family={"G":"A","Z":"B","O":"C"}.get(family,family)
    if family=="A":
        candidates=response_json.get("candidates") or []
        if not candidates: raise ValueError("Gemini response has no candidates")
        parts=candidates[0].get("content",{}).get("parts",[])
        text="".join(p.get("text","") for p in parts if isinstance(p,dict))
        return {"raw_text":text,"finish_reason":candidates[0].get("finishReason"),"usage":response_json.get("usageMetadata"),"provider_model":response_json.get("modelVersion"),"provider_request_id":response_json.get("responseId")}
    choices=response_json.get("choices") or []
    if not choices: raise ValueError("Chat Completions response has no choices")
    message=choices[0].get("message",{})
    content=message.get("content")
    if not isinstance(content,str): raise ValueError("provider message content is not plain text")
    return {"raw_text":content,"finish_reason":choices[0].get("finish_reason"),"usage":response_json.get("usage"),"provider_model":response_json.get("model"),"provider_request_id":response_json.get("id")}

def dispatch_free_only(request:Request,provider_config:dict,timeout_seconds:int=60,opener=urlopen,raw_sink=None)->dict:
    """The only supported network entry point; requires all three Free/no-overage attestations."""
    assert_free_only_entitlements(provider_config)
    return dispatch(request,timeout_seconds=timeout_seconds,opener=opener,raw_sink=raw_sink)
