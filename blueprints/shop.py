from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify
import requests
shop_bp = Blueprint("shop", __name__, url_prefix='/shop')
@shop_bp.route("/jumia")
def jumia_info():
    query = request.args.get("query")
    if not query:
        return jsonify({
            'status': 400,
            'message': 'Missing required query parameter.'
        }),400
    response = requests.get(f"https://www.jumia.com.ng/catalog/?q={query}")
    if not response.ok:
        return jsonify({
            'status': 500,
            'message':"Internal Server Error"
        }),500
    soup = BeautifulSoup(response.text, "html.parser")
    check_available = soup.find("h2",class_="-pvs -fs16 -m -ow-a")
    if check_available is None:
        return jsonify({
            'status':404,
            'message':'Product Not found Try a different product'
        }),404
    product = soup.find("h2",class_="name")
    product_price = soup.find()

