# Free Model Discovery on Nous Portal

## Context

Nous Portal (provider key: `nous`) offers both free and paid models. There is no UI to filter by free tier — you must query the API directly.

## Discovering Free Models

```bash
curl -s -H "Accept: application/json" \
  "https://inference-api.nousresearch.com/v1/models" \
  | python3 -c "import sys,json; data=json.load(sys.stdin); [print(m['id']) for m in data.get('data',[]) if ':free' in m['id']]"
```

This returns only models with the `:free` suffix. Current free models as of this writing:

- `poolside/laguna-s-2.1:free`
- `upstage/solar-pro4:free`
- `inclusionai/ling-3.0-flash-sante:free`
- `inclusionai/ling-3.0-flash-fin:free`
- `poolside/laguna-xs-2.1:free`
- `stepfun/step-3.7-flash:free`
- `meituan/longcat-2.0:free`

## Nemotron Models

All `nvidia/nemotron-*` models require credits — none are free:

- `nvidia/nemotron-3-ultra-550b-a55b` — paid (requires credits)
- `nvidia/nemotron-3-super-120b-a12b` — paid
- `nvidia/nemotron-3-nano-30b-a3b` — paid
- `nvidia/nemotron-3.5-lightning` — paid

If the user asks for "the best free Nemotron model," there is no such option. Redirect to `poolside/laguna-s-2.1:free` as the best available free alternative.

## Switching a Bot to a Free Model

```bash
hermes config set model.default poolside/laguna-s-2.1:free --profile <bot-name>
hermes config set model.provider nous --profile <bot-name>
```

Then verify in the config file that the `model:` section looks like:

```yaml
model:
  default: poolside/laguna-s-2.1:free
  provider: nous
  base_url: ''
```

The provider key MUST be `nous` (not `nous-portal`) — this maps to Nous Portal's inference API.

## Verification

```bash
hermes -p <bot-name> chat -q "hello" --max-turns 1
```

Should return a response in under 10 seconds if the model is reachable and free.
