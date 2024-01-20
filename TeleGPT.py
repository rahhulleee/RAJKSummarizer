from openai import OpenAI
import os
import configparser

curr_dir = os.getcwd()
config = configparser.ConfigParser()
config.read(os.path.join(curr_dir, "telethon.config"))

api_id = config["telethon_credentials"]["chatgpt_api_key"] 

client = OpenAI(api_key=api_id)

# Use GPT API
# change max_tokens to change length of response
def chatGPT(prompt, model="gpt-3.5-turbo", max_tokens=75, stop=None):
    response = client.chat.completions.create(
        model=model,
        messages = [{"role": "user", "content": prompt}],  # Provide the required 'messages' argument,
        max_tokens=max_tokens,
        stop=stop
        )
    return response.choices[0].message.content.strip()

def TeleGPT(df, question):
    # join all text messages together
    joined_text = []
    for i in range(len(df)):
        if df.iloc[i]["text"] is not None:
            joined_text.append(df.iloc[i]["text"])
    joined_text = " ".join(joined_text)
  
    # Extract relevant text
    prompt = question + "".join(joined_text)
    print("Prompt Created!")
    print("Computing...")
    return chatGPT(prompt)
