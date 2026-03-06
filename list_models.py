import google.generativeai as genai

genai.configure(api_key='AIzaSyDX4E8DQi5-HBfBMpnLXudQZz4GOzi0GBo')

try:
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print("Error listing models:", e)
