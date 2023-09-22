from flask import Flask, render_template, request, jsonify
import openai
import os
import sqlite3
import trafilatura
import validators

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = "The following body of text is a company's privacy policy outlining how they handle personal and private information from a consumer. Outline key points and present them in a short and succinct bullet list. Use '~*' characters to indicate the bullet points. Focus on privacy infringements and shady practices. The 5 main bullet point topics to cover are what specific information is being collected on the user, how this information is stored, who this information is shared with, whether profit is made from this information and/or it is sold and how long this information is stored for, along with whether you can request for its deletion. Please provide a sixth bullet point describe the most invasively collected data. Please provide examples of the most egregious and privacy breaking data collections outlined in the policy. The company's privacy policy is as follows: "

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    print('query called')
    
    if request.method == 'GET':
        textInput = request.args.get('textInput')
    elif request.method == 'POST':
        textInput = request.form['textInput']
    
    if validators.url(textInput):
        downloaded = trafilatura.fetch_url('https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ')
        textInput = trafilatura.extract(downloaded)

        if len(textInput) < 1000:
            return jsonify(content='Error: html page could not be read, please user alternate method')

    messages = [{"role": "user", "content": (prompt + textInput)}]

    try:
        print('sending')
        response = openai.ChatCompletion.create(
            #model='gpt-3.5-turbo-16k', 
            model='gpt-4',
            messages=messages
        )
        content = response.choices[0].message["content"]
    except openai.error.RateLimitError:
        content = "Rate limit has been reached, please try again later."
    except:
        content = "Error has occured, please contact administrator."
    
    content = content.replace('~*', '<br>-')

    return jsonify(content=content)

if __name__ == '__main__':
    app.run(debug=True)