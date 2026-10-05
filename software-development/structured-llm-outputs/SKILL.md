---
name: structured-llm-outputs
description: "Pydantic-typed LLM outputs with retries (instructor)."
version: 1.0.0
author: Hermes Agent (ported from 567-labs/instructor, MIT; run live against a scripted local server)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llm, structured-output, pydantic, validation, retries, testing, instructor]
    related_skills: [python-craft, test-driven-development, verification-before-completion, fastmcp, regex-vs-llm-structured-text]
---

<!-- source: 567-labs/instructor (MIT); instructor 1.17.0 + openai 3.3.0 + pydantic 2.13.5 in a uv Python 3.12 venv on Windows; every behaviour below was run against a local fake OpenAI-compatible server, no real API key or provider -->

# Structured LLM outputs (instructor + Pydantic)

## What This Skill Does

`instructor` patches an LLM client so that `create(..., response_model=MyModel)` returns a validated Pydantic object instead of text. It sends the model's JSON schema as a forced tool call,
validates the reply, and on a validation error **re-asks the model with the error attached**, up to `max_retries`. Use it whenever an LLM must produce data that code consumes.

## When to Use

- Extracting entities, classifications, or tables from text into typed objects; any place you would otherwise `json.loads` a model reply and hope
- You want validation rules (ranges, formats, business logic) enforced with automatic repair attempts
- Not for free-form prose, or where a regex or parser is enough (`regex-vs-llm-structured-text`)

## Basic use

```python
import instructor, openai
from pydantic import BaseModel, Field, field_validator

client = instructor.from_openai(openai.OpenAI())          # other provider adapters exist (from_provider, ...)

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)
    @field_validator("name")
    @classmethod
    def capitalised(cls, v):
        if not v[:1].isupper():
            raise ValueError("name must start with a capital letter")
        return v

user = client.chat.completions.create(model="gpt-4o-mini", response_model=User, max_retries=2,
                                      messages=[{"role": "user", "content": "Extract: jason is 25"}])
user, raw = client.chat.completions.create_with_completion(model="gpt-4o-mini", response_model=User,
                                      messages=[{"role": "user", "content": "Extract: jason is 25"}])   # also returns the raw completion
```

## Verified behaviour (scripted server, instructor 1.17.0)

| Scenario | Observed |
|---|---|
| Valid first reply | 1 request; result `name='Jason' age=25` |
| What is sent | a tool named after the model (`User`) with the model's property schema (`name`, `age`) and `tool_choice` forcing `{"type":"function","function":{"name":"User"}}` |
| Invalid first reply (`name: "jason"`), valid second | **2 requests**. The retry request contains the original `user` message, the model's own invalid `assistant` tool call, and a `tool` message: `Validation Error found: 1 validation error for User / name / Value error, name must start with a capital letter [...]` |
| Field constraint (`age: 200` with `le=120`), then a valid reply | fixed on the second request (`age=30`) |
| Always invalid with `max_retries=1` | 2 requests total, then `InstructorRetryException` whose text begins `Max retries exceeded. Total attempts: 2, Last error: 1 validation error...` and includes the failed attempts |
| `max_retries=0`, invalid reply | 1 request, `InstructorRetryException` (`Total attempts: 1`) |
| `create_with_completion` | returns `(parsed, raw)`; `raw.usage.total_tokens` was 15 in the scripted reply |
| Nested `List[User]` inside a wrapper model | parsed to the list of validated objects |

So `max_retries=N` means up to `N + 1` calls: **budget tokens and latency accordingly**, and remember each retry repeats the whole conversation plus the failed output.

## Testing LLM code without an API: a scripted fake server

A deterministic test double for any OpenAI-compatible client code, about 25 lines of stdlib: an `http.server` handler that records each request body and replies from a scripted list (here with a tool-call reply).

```python
import json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

REQS, SCRIPT = [], []

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        REQS.append(body)
        args = SCRIPT.pop(0)
        tool = body["tools"][0]["function"]["name"]
        msg = {"role": "assistant", "content": None,
               "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": tool, "arguments": json.dumps(args)}}]}
        out = {"id": "c1", "object": "chat.completion", "created": 0, "model": body["model"],
               "choices": [{"index": 0, "message": msg, "finish_reason": "tool_calls"}],
               "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

srv = HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
client = instructor.from_openai(openai.OpenAI(base_url=f"http://127.0.0.1:{srv.server_address[1]}/v1", api_key="test"))
```

Script `SCRIPT[:] = [bad, good]`, call the client, then assert on `len(REQS)` and on the retry messages. This makes retry counts, error wording and schema generation testable in CI at zero cost.

## Rules

- Put business rules in Pydantic validators, with error messages written for the model to read (the message is fed back verbatim).
- Keep response models small and descriptive (`Field(description=...)`); every field and description is sent to the model as schema.
- Use `max_retries` of 1 to 3, catch `InstructorRetryException`, and treat exhausted retries as a normal failure path, not a crash.
- Never trust extracted values blindly for consequential actions: validate against ground truth where possible (`verification-before-completion`).
- Pin `instructor`, `openai` and `pydantic` versions: provider adapters and schema generation change across releases (`openai` was 3.3.0 here, a new major relative to older tutorials).

## Pitfalls

- Retries multiply cost; a vague validator can burn several calls per item.
- A model that cannot satisfy a constraint will fail every retry: loosen the constraint or give it the missing information.
- Streaming and partial-model features exist but were not exercised here.

## Verification

Run the fake-server test: valid reply = 1 request; invalid then valid = 2 requests with a `tool` message beginning `Validation Error found`; exhausted retries raise `InstructorRetryException`.
