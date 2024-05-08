from flask import Flask, render_template, request
from forms import SignUpForm
from processing import Processing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello'

@app.route('/', methods = ['GET', 'POST'])
def home():
    form = SignUpForm()
    if form.is_submitted():
        result = request.form
        ticker = result['ticker']
        print(ticker)
        process(ticker)
        return render_template('process.html', result = result)
    return render_template('index.html', form = form)

def process(ticker):
    process = Processing(ticker)
    return ticker

if __name__ == "__main__":
    app.run()


# Source for this file, forms, index.html, and process.html comes heavily from TheCodex YT channel.