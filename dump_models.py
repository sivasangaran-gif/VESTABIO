import google.generativeai as genai
import json

genai.configure(api_key='AIzaSyDX4E8DQi5-HBfBMpnLXudQZz4GOzi0GBo')
models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
with open('models.json', 'w') as f:
    json.dump(models, f)
