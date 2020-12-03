from flask import Flask, render_template, redirect
from scrape_mars import scrape
import pymongo

app = Flask(__name__)


@app.route('/scrape')
def go_scrape():
    # retrieve data
    scrape()
    # go to index
    return redirect('/')

@app.route('/')
def index():
    # connect to mongo
    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client.mars_db
    # retrieve one record
    data = db.mars.find_one()
    # send data to populate html
    return render_template('index.html', data = data)


if __name__ == "__main__":
    app.run(debug=True)
