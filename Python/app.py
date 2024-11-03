from flask import Flask, request, render_template_string
import datetime
import socket
import netifaces as ni
from functools import wraps

app = Flask(__name__)

def get_mac_address():
    """Get MAC address with better error handling"""
    try:
        for iface in ni.interfaces():
            addresses = ni.ifaddresses(iface)
            if ni.AF_LINK in addresses:
                mac = addresses[ni.AF_LINK][0]['addr']
                if mac and mac != "00:00:00:00:00:00":
                    return mac
    except Exception as e:
        return f"MAC Unavailable: {str(e)}"
    return "MAC Address Not Found"

def error_handler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    return decorated_function

@app.route('/')
@error_handler
def user_info():
    # Get real IP even behind proxy
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Get username with fallback
    username = request.headers.get('Username', 'Guest')
    
    # Get MAC address
    mac_address = get_mac_address()
    
    # Get timestamp in UTC
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Information</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .info-container { 
                border: 1px solid #ddd; 
                padding: 20px;
                border-radius: 5px;
            }
            .success { color: green; }
        </style>
    </head>
    <body>
        <div class="info-container">
            <h2>System Information</h2>
            <p><b>IP Address:</b> {{ ip }}</p>
            <p><b>MAC Address:</b> {{ mac }}</p>
            <p><b>Username:</b> {{ username }}</p>
            <p><b>Timestamp:</b> {{ timestamp }}</p>
            <br>
            <h3 class="success">Assignment completed successfully!</h3>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(
        html_template,
        ip=user_ip,
        mac=mac_address,
        username=username,
        timestamp=timestamp
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)