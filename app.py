from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import openai
import os
import trafilatura
import validators

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pastqueries.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class pastQuery(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    inputUrl = db.Column(db.String(200), nullable=True, unique=True)
    outputText = db.Column(db.String(1500), nullable=False)

    def __init__(self, inputUrl, outputText):
        self.inputUrl = inputUrl
        self.outputText = outputText

with app.app_context():
    db.create_all()

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
        savedURL = textInput

        dbtext = pastQuery.query.filter_by(inputUrl = textInput).first()
        if dbtext:
            print("Already searched, delivering from db")
            return jsonify(content=dbtext.outputText)

        print("This is new")
        downloaded = trafilatura.fetch_url(textInput)
        textInput = trafilatura.extract(downloaded)

        if len(textInput) < 1000:
            return jsonify(content='Error: html page could not be read, please user alternate method')

    messages = [{"role": "user", "content": (prompt + textInput)}]

    try:
        print('sending')
        response = openai.ChatCompletion.create(
            # change model to gpt3.5 when testing to save money
            #model='gpt-3.5-turbo-16k', 
            model='gpt-4',
            messages=messages
        )
        content = response.choices[0].message["content"]
    except openai.error.RateLimitError:
        content = "Rate limit has been reached, please try again later."
        return jsonify(content=content)
    except openai.error.APIError:
        content = "API error"
        return jsonify(content=content)
    except openai.error.Timeout:
        content = "Timeout error"
        return jsonify(content=content)
    except openai.error.APIConnectionError:
        content = "Connection error"
        return jsonify(content=content)
    except openai.error.InvalidRequestError:
        content = "Invalid request error"
        return jsonify(content=content)
    except openai.error.AuthenticationError:
        content = "Authentication error"
        return jsonify(content=content)
    except openai.error.PermissionError:
        content = "Permission error"
        return jsonify(content=content)
    except openai.error.ServiceUnavailableError:
        content = "Service unavailable error"
        return jsonify(content=content)
    except:
        print("error:", openai.error)
        content = "Error has occured, please contact administrator."
        return jsonify(content=content)
    
    content = content.replace('~*', '<br>-')

    newQuery = pastQuery(savedURL, content)
    db.session.add(newQuery)
    db.session.commit()

    return jsonify(content=content)

if __name__ == '__main__':
    app.run(debug=True)