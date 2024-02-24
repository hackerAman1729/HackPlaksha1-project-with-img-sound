from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from openai import OpenAI
from exa_py import Exa

app = Flask(__name__)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
exa_client = Exa(api_key=os.getenv('EXA_API_KEY'))

def generate_random_topic():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a knowledgeable assistant."},
            {"role": "user", "content": "Suggest a random interesting topic. random topic like from rocket propulsion, to nylon thread, to history topic, to some historic sport event, to lithium mining to essential proteins etc etc. The topics should not be limited to that as I just mentioned them as an example like how niche the topics can be. Just give the topic and say nothing else."}
        ]
    )
    topic = response.choices[0].message.content.strip()
    return topic

def get_resources(topic):
  try:
      results = exa_client.search_and_contents(topic, use_autoprompt=True, num_results=1, text=True)
      if results.results and len(results.results) > 0:
          content = results.results[0].text  # Text content
          url = results.results[0].url  # URL of the source
          return content, url
      else:
          return "No content found for the given topic.", ""
  except Exception as e:
      print(f"Error fetching resources from Exa: {e}")
      return "An error occurred while fetching resources.", ""





def summarize_content(content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": f"Summarize this in 150 words, make sure that you keep it concise yet interesting, factfully correct: {content}"}
        ]
    )
    summary = response.choices[0].message.content.strip()
    return summary

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_topic', methods=['GET'])
def get_topic():
    topic = generate_random_topic()
    content, url = get_resources(topic)
    if content:
        summary = summarize_content(content)
    else:
        summary = "Could not find sufficient resources for the generated topic."
    return jsonify({'topic': topic, 'summary': summary, 'url': url})


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80,debug=True)
