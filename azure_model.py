from openai import OpenAI

import keys


PROJECT_ENDPOINT = "https://lumiere-resource.services.ai.azure.com/api/projects/lumiere"
MODEL_DEPLOYMENT = "gpt-5.4-mini"

client = OpenAI(
    api_key=keys.api_key_azure,
    base_url=f"{PROJECT_ENDPOINT}/openai/v1/",
)


def generate_text(prompt, max_output_tokens):
    response = client.responses.create(
        model=MODEL_DEPLOYMENT,
        input=prompt,
        reasoning={"effort": "low"},
        max_output_tokens=max_output_tokens,
    )
    return response.output_text


def generate_json(prompt, schema, max_output_tokens):
    response = client.responses.create(
        model=MODEL_DEPLOYMENT,
        input=prompt,
        reasoning={"effort": "low"},
        max_output_tokens=max_output_tokens,
        text={
            "format": {
                "type": "json_schema",
                "name": "structured_response",
                "strict": True,
                "schema": schema,
            }
        },
    )
    return response.output_text