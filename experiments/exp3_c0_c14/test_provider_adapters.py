import json
import unittest
from provider_adapters import build_request, extract_text, assert_free_only_entitlements, dispatch_free_only

class ProviderAdapterTests(unittest.TestCase):
    def test_gemini_key_is_header_not_url(self):
        provider={"model":"gemini-2.5-flash","base_url":"https://generativelanguage.googleapis.com/v1beta","credential_env":"GEMINI_API_KEY"}
        req=build_request("A",provider,[{"role":"user","content":"hello"}],{"GEMINI_API_KEY":"secret-test"})
        self.assertNotIn("secret-test",req.full_url)
        self.assertEqual(req.get_header("X-goog-api-key"),"secret-test")
        body=json.loads(req.data)
        self.assertEqual(body["contents"][0]["parts"][0]["text"],"hello")

    def test_cloudflare_account_id_resolved_locally(self):
        provider={"model":"@cf/zai-org/glm-4.7-flash","base_url":"https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/ai/v1","credential_env":"CLOUDFLARE_API_TOKEN"}
        env={"CLOUDFLARE_API_TOKEN":"secret-test","CLOUDFLARE_ACCOUNT_ID":"account-123"}
        req=build_request("B",provider,[{"role":"user","content":"hello"}],env)
        self.assertIn("/accounts/account-123/ai/v1/chat/completions",req.full_url)
        self.assertNotIn("secret-test",req.full_url)

    def test_groq_openai_compatible_request(self):
        provider={"model":"openai/gpt-oss-120b","base_url":"https://api.groq.com/openai/v1","credential_env":"GROQ_API_KEY"}
        req=build_request("C",provider,[{"role":"user","content":"hello"}],{"GROQ_API_KEY":"secret-test"})
        self.assertEqual(req.full_url,"https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(req.get_header("Authorization"),"Bearer secret-test")

    def test_missing_secret_fails_before_network(self):
        provider={"model":"gemini-2.5-flash","base_url":"https://example.invalid/v1","credential_env":"GEMINI_API_KEY"}
        with self.assertRaisesRegex(RuntimeError,"missing"):
            build_request("A",provider,[{"role":"user","content":"x"}],{})

    def test_free_entitlement_gate_blocks_example_config(self):
        config={"defaults":{"api_spend_usd_max":0,"paid_fallback":False},"provider_families":{"A":{},"B":{},"C":{}}}
        with self.assertRaisesRegex(RuntimeError,"not verified"):
            assert_free_only_entitlements(config)

    def test_gemini_response_extracts_only_final_text(self):
        result=extract_text("A",{"candidates":[{"content":{"parts":[{"text":"{\"ok\":true}"}]},"finishReason":"STOP"}],"usageMetadata":{"promptTokenCount":3}})
        self.assertEqual(result["raw_text"],'{"ok":true}')
        self.assertEqual(result["finish_reason"],"STOP")

    def test_chat_response_extracts_only_message_content(self):
        result=extract_text("C",{"id":"req1","model":"openai/gpt-oss-120b","choices":[{"message":{"content":"{\"ok\":true}"},"finish_reason":"stop"}],"usage":{"prompt_tokens":2}})
        self.assertEqual(result["raw_text"],'{"ok":true}')
        self.assertEqual(result["provider_request_id"],"req1")


    def test_free_dispatch_requires_all_three_verified_accounts_before_network(self):
        class NeverCall:
            def __call__(self,*args,**kwargs):
                raise AssertionError("network must not be reached")
        provider={"model":"gemini-2.5-flash","base_url":"https://example.invalid/v1","credential_env":"GEMINI_API_KEY"}
        request=build_request("A",provider,[{"role":"user","content":"test"}],{"GEMINI_API_KEY":"test"})
        config={"defaults":{"api_spend_usd_max":0,"paid_fallback":False},"provider_families":{x:{"account_free_tier_verified":True,"billing_state":"free_no_paid_overage","quota_verified":True} for x in ("A","B","C")}}
        # The gate passes, then a fake transport deliberately returns a synthetic response.
        class FakeResponse:
            status=200
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def read(self): return b'{"candidates":[{"content":{"parts":[{"text":"ok"}]}}]}'
        result=dispatch_free_only(request,config,opener=lambda *a,**k:FakeResponse())
        self.assertEqual(result["http_status"],200)
        config["provider_families"]["B"]["quota_verified"]=False
        with self.assertRaisesRegex(RuntimeError,"quota"):
            dispatch_free_only(request,config,opener=NeverCall())

    def test_original_routing_codes_alias_to_provider_adapters(self):
        gemini={"model":"gemini-2.5-flash","base_url":"https://generativelanguage.googleapis.com/v1beta","credential_env":"GEMINI_API_KEY"}
        groq={"model":"openai/gpt-oss-120b","base_url":"https://api.groq.com/openai/v1","credential_env":"GROQ_API_KEY"}
        g=build_request("G",gemini,[{"role":"user","content":"x"}],{"GEMINI_API_KEY":"k"})
        o=build_request("O",groq,[{"role":"user","content":"x"}],{"GROQ_API_KEY":"k"})
        self.assertIn("generateContent",g.full_url)
        self.assertIn("chat/completions",o.full_url)


if __name__=="__main__": unittest.main()
