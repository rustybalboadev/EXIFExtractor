import os
from pprint import pprint
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/saved_photos"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == "GET":
        def dataList():
            return ['Data Will Show Here']
        return render_template('index.html', dataList=dataList, lat=37.78469, long=-482.472367)
    elif request.method == 'POST':
        file_ = request.files['file']

        if file_.filename == '':
            flash("No Selected File")
        if file_ and allowed_file(file_.filename):
            filename = secure_filename(file_.filename)
            file_.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = Image.open(os.path.dirname(os.path.abspath(__file__)) + "/saved_photos/" + filename)
            image.verify()
            exif = image._getexif()
            if exif:
                labeled={}
                for (key, val) in exif.items():
                    labeled[TAGS.get(key)] = val

                for key in labeled['GPSInfo'].keys():
                    name = GPSTAGS.get(key, key)
                    labeled['GPSInfo'][name] = labeled['GPSInfo'].pop(key)

                for key in ['Latitude', 'Longitude']:
                    g = labeled['GPSInfo'][f'GPS{key}']
                    ref = labeled['GPSInfo'][f'GPS{key}Ref']
                    labeled[key] = ( g[0][0]/g[0][1] +
                                    g[1][0]/g[1][1] / 60 +
                                    g[2][0]/g[2][1] / 3600
                                    ) * (-1 if ref in ['S','W'] else 1)
                date = labeled['DateTime']
                make = labeled['Make']
                model = labeled['Model']
                latitude = labeled['Latitude']
                longitude = labeled['Longitude']
                data = ["Time: " + str(date), "Make: " + str(make), "Model: " + str(model), "Lat: " + str(latitude), "Long: " + str(longitude)]
                def dataList():
                    return data
                os.remove(os.path.dirname(os.path.abspath(__file__)) + "/saved_photos/" + filename)
                return render_template('index.html', dataList=dataList, lat=latitude, long=longitude)
            else:
                def dataList():
                    return ['No Exif Data']
                os.remove(os.path.dirname(os.path.abspath(__file__)) + "/saved_photos/" + filename)
                return render_template('index.html', dataList=dataList, lat=37.78469, long=-482.472367)
        def dataList():
            return ['Unsupported File Type']
        return render_template('index.html', dataList=dataList, lat=37.78469, long=-482.472367)

if __name__ == "__main__":
    app.run()