from app.webhook.routes import app_instance

if __name__ == "__main__":
    app_instance.run(port=5000, debug=True)
