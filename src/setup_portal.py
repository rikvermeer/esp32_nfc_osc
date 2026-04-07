import socket
import machine
from config import save_config

HTML_FORM = """<!DOCTYPE html>
<html>
<head>
    <title>NFC OSC Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>NFC OSC Configuration</h1>
    <form method="POST" action="/save">
        <h2>WiFi Settings</h2>
        <label>SSID:</label><br>
        <input type="text" name="wifi_ssid" value="{wifi_ssid}" required><br><br>
        <label>Password:</label><br>
        <input type="password" name="wifi_password" value="{wifi_password}" required><br><br>
        
        <h2>OSC Settings</h2>
        <label>Server IP:</label><br>
        <input type="text" name="osc_server_ip" value="{osc_server_ip}" required><br><br>
        <label>Server Port:</label><br>
        <input type="number" name="osc_server_port" value="{osc_server_port}" required><br><br>
        
        <button type="submit">Save &amp; Reboot</button>
    </form>
</body>
</html>
"""

HTML_SUCCESS = """<!DOCTYPE html>
<html>
<head>
    <title>Success</title>
    <meta http-equiv="refresh" content="3;url=/">
</head>
<body>
    <h1>Configuration Saved!</h1>
    <p>Device will reboot in 3 seconds...</p>
</body>
</html>
"""

def parse_post_data(data):
    """Parse POST form data"""
    params = {}
    try:
        body = data.split('\r\n\r\n')[1]
        pairs = body.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                # URL decode
                value = value.replace('+', ' ')
                value = value.replace('%40', '@')
                value = value.replace('%2F', '/')
                value = value.replace('%3A', ':')
                params[key] = value
    except Exception as e:
        print(f"Error parsing POST data: {e}")
    return params

def validate_config(params):
    """Validate configuration parameters"""
    required = ['wifi_ssid', 'wifi_password', 'osc_server_ip', 'osc_server_port']
    for field in required:
        if field not in params or not params[field]:
            return False, f"Missing field: {field}"
    
    # Validate port is a number
    try:
        int(params['osc_server_port'])
    except ValueError:
        return False, "OSC port must be a number"
    
    return True, "OK"

def run_setup_portal(ap):
    """Run blocking HTTP server for web-based configuration"""
    print("Starting setup portal on http://192.168.4.1")
    
    # Get current config for form defaults
    from config import load_config
    current_config = load_config()
    
    # Create socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    
    print("Setup portal listening on port 80")
    print("Connect to WiFi network and navigate to http://192.168.4.1")
    
    while True:
        try:
            cl, addr = s.accept()
            print(f"Client connected from {addr}")
            
            # Read request
            request = cl.recv(1024).decode('utf-8')
            print(f"Request: {request[:100]}")
            
            # Parse request
            if 'GET / ' in request or 'GET /index' in request:
                # Show form
                html = HTML_FORM.format(
                    wifi_ssid=current_config.get('wifi_ssid', ''),
                    wifi_password=current_config.get('wifi_password', ''),
                    osc_server_ip=current_config.get('osc_server_ip', ''),
                    osc_server_port=current_config.get('osc_server_port', 11000)
                )
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html
                cl.send(response.encode('utf-8'))
                
            elif 'POST /save' in request:
                # Parse form data
                params = parse_post_data(request)
                print(f"Received config: {params}")
                
                # Validate
                valid, message = validate_config(params)
                if valid:
                    # Save config
                    new_config = {
                        'wifi_ssid': params['wifi_ssid'],
                        'wifi_password': params['wifi_password'],
                        'osc_server_ip': params['osc_server_ip'],
                        'osc_server_port': int(params['osc_server_port']),
                        'ap_ssid': current_config.get('ap_ssid', 'NFC-SETUP'),
                        'ap_password': current_config.get('ap_password', '12345678')
                    }
                    
                    if save_config(new_config):
                        # Send success page
                        response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + HTML_SUCCESS
                        cl.send(response.encode('utf-8'))
                        cl.close()
                        s.close()
                        
                        print("Configuration saved successfully, rebooting...")
                        machine.reset()
                    else:
                        error_html = '<html><body><h1>Error saving config</h1><a href="/">Back</a></body></html>'
                        response = 'HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n' + error_html
                        cl.send(response.encode('utf-8'))
                else:
                    error_html = f'<html><body><h1>Validation Error</h1><p>{message}</p><a href="/">Back</a></body></html>'
                    response = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n' + error_html
                    cl.send(response.encode('utf-8'))
            else:
                # 404
                response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Not Found</h1></body></html>'
                cl.send(response.encode('utf-8'))
            
            cl.close()
            
        except Exception as e:
            print(f"Error handling request: {e}")
            try:
                cl.close()
            except:
                pass
