from flask_wtf.csrf import csrf_exempt

@api_bp.route('/endpoint', methods=['POST'])
@csrf_exempt
def api_endpoint():
    # Your API logic here
    pass