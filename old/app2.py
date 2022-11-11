import os

from flask import Flask

app = Flask(__name__)

@app.route('/n')
def get_data():
    return 'ok'


@app.route('/na')
async def async_get_data():
    return 'ok'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port)