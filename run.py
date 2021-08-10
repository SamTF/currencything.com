### Simple barebones script to run the website

from website import app

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=80)

