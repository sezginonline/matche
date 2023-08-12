from app.app import app

if __name__ == "__main__":
    ssl = {"cert": "/opt/homebrew/etc/httpd/server.crt", "key": "/opt/homebrew/etc/httpd/server.key"}
    app.run(host="127.0.0.1", port=8000, ssl=None, fast=True, debug=False, access_log=False)
