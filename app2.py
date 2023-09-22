from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = "The following body of text is a company's privacy policy outlining how they handle personal and private information from a consumer. Outline key points and present them in a short and succinct bullet list. Focus on privacy infringements and shady practices. The 5 main bullet point topics to cover are what specific information is being collected on the user, how this information is stored, who this information is shared with, whether profit is made from this information and/or it is sold and how long this information is stored for, along with whether you can request for its deletion. Please provide a sixth bullet point describe the most invasively collected data. Please provide examples of the most egregious and privacy breaking data collections outlined in the policy. The company's privacy policy is as follows: "

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'GET':
        textInput = request.args.get('textInput')
    elif request.method == 'POST':
        textInput = request.form['textInput']

    messages = [{"role": "user", "content": (prompt + textInput)}]

    try:
        response = openai.ChatCompletion.create(model='gpt-4', messages=messages)
        content = response.choices[0].message["content"]
    except openai.error.RateLimitError:
        content = "Rate limit has been reached, please try again later."
    except:
        content = "Error has occured, please contact administrator."

    return jsonify(content=content)

if __name__ == '__main__':
    app.run(debug=True)