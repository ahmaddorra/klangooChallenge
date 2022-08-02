from flask import Flask, jsonify, request
from affiliateMarketing.main import LinkedinScraper
from threading import Thread
import logging, json
import sys
import uuid
# Create and configure logger using the basicConfig() function


#app = Flask(__name__)
data= None

#@app.route("/test-api", methods=["GET"])
#def test_api():
#    print("~~~~~~~~~~~~~~~~~~~~> In~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`> ")
#    return "Hello World."


# @app.route("/")
# def home_view():
#     return "<h1>Welcome to linkedin Scraper.</h1>"


#@app.route("/", methods=["POST"])
def get_scrapped_data(email, id = None):
    global data
    print("start" + "~~~~~~" * 10, file=sys.stderr)
    
    if id is not None:
        return data.get('id', {'message':'data is not yet ready'})
    else:
        new_id = uuid.uuid4()
        url = "https://www.linkedin.com/sales/ssi"
        
        list_name = email + new_id
        print("~~~~~~" * 10, file=sys.stderr)

        print("~~~~~~> url", url, file=sys.stderr)
        print("~~~~~~" * 10, file=sys.stderr)
        scrapping_obj = LinkedinScraper(url)
        thread = Thread(target=scrapping_obj.get_scraped_data(url, email,list_name, new_id), args=())
        thread.start()

        # data[]= scrapping_obj.get('data')

        status_code = 200
        response = {"id": new_id}
    return jsonify(response), status_code


#if __name__ == "__main__":
#    app.run(debug=True, host="0.0.0.0",port=5000)
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

