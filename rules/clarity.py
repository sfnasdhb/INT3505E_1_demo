from flask import Blueprint, jsonify, request
from datetime import datetime
from data import ORDERS

bp = Blueprint("clarity", __name__)

# Viết rõ ràng, dễ hiểu
@bp.get("/good/orders")
def good_list_orders():
    """
    /api/clarity/good/orders?created_date_after=YYYY-MM-DD
    """
    created_date_after = request.args.get("created_date_after")
    results = ORDERS
    if created_date_after:
        try:
            threshold = datetime.strptime(created_date_after, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"detail": "created_date_after must be YYYY-MM-DD"}), 400
        results = [
            o for o in ORDERS
            if datetime.strptime(o["created_date"], "%Y-%m-%d").date() > threshold
        ]
    return jsonify(results)

# Viết tắt mơ hồ, các trường khó hiểu
@bp.get("/bad/svc/usr/<int:id>/invs")
def bad_invoices(id: int):
    return jsonify({"u_name": f"user-{id}", "ts_upd": 1672531200})
