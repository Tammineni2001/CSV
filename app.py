from routes.kpi_blueprint import kpi_blueprint
from flask import Flask
from routes.csv_bp import csv_blueprint
from routes.csv1_bp import csv1_blueprint

app = Flask(__name__)
app.register_blueprint(kpi_blueprint, url_prefix="/api/kpi")
app.register_blueprint(csv_blueprint, url_prefix="/api/csv")
app.register_blueprint(csv1_blueprint, url_prefix="/api/csv1")

if __name__ == "__main__":
    app.run(debug=True)
