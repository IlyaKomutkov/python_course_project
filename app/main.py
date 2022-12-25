from app import app
from viz import layout
import callbacks

app.layout = layout
server = app.server

if __name__ == '__main__':
	app.run_server(debug=True, host='0.0.0.0', port=8050)
