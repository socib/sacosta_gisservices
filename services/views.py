# -*- coding:utf-8 -*-

from flask import Blueprint, jsonify, current_app, abort, send_file, request
from decorators.crossdomain import crossdomain

import utils
import gisdata
import maputils
import reporting

app = Blueprint('services', __name__, template_folder='templates')


@app.route('/api/v1.0/sacosta/<polygon_text>', methods=['GET'])
@app.route('/api/v1.0/sacosta/', methods=['POST'])
@crossdomain(origin='*')
def get_sacosta_polygon(polygon_text=None):
    if request.method == 'POST':
        polygon_text = request.form['polygon']

    try:
        polygon = utils.create_polygon(polygon_text)
    except ValueError, e:
        return jsonify({'error': str(e)})
    return utils.send_json_data(gisdata.get_data_sacosta(current_app.config, polygon))


@app.route('/api/v1.0/sacosta/<float:xmin>/<float:ymin>/<float:xmax>/<float:ymax>', methods=['GET'])
@crossdomain(origin='*')
def get_sacosta_bbox(xmin, ymin, xmax, ymax):
    polygon = utils.create_polygon("%f,%f,%f,%f,%f,%f,%f,%f" % (xmin, ymin, xmin, ymax, xmax, ymax, xmax, ymin))
    return utils.send_json_data(gisdata.get_data_sacosta(current_app.config, polygon))


@app.route('/api/v1.0/proteccion/<polygon_text>', methods=['GET'])
@app.route('/api/v1.0/proteccion/', methods=['POST'])
@crossdomain(origin='*')
def get_proteccion_polygon(polygon_text=None):
    if request.method == 'POST':
        polygon_text = request.form['polygon']

    try:
        polygon = utils.create_polygon(polygon_text)
    except ValueError, e:
        return jsonify({'error': str(e)})
    return utils.send_json_data(gisdata.get_data_proteccion(current_app.config, polygon))


@app.route('/api/v1.0/uso-humano/<polygon_text>', methods=['GET'])
@app.route('/api/v1.0/uso-humano/', methods=['POST'])
@crossdomain(origin='*')
def get_usohumano_polygon(polygon_text=None):
    if request.method == 'POST':
        polygon_text = request.form['polygon']

    try:
        polygon = utils.create_polygon(polygon_text)
    except ValueError, e:
        return jsonify({'error': e})
    return utils.send_json_data(gisdata.get_data_usohumano(current_app.config, polygon))


@app.route('/sacosta/map/<polygon_text>/<int:size_x>x<int:size_y>/tile.png', methods=['GET'])
@crossdomain(origin='*')
def sacosta_map_tile(polygon_text, size_x, size_y):
    try:
        polygon = utils.create_polygon(polygon_text)
    except ValueError:
        abort(404)

    layers = current_app.config['MAP_LAYERS']['sacosta']
    img = maputils.generate_map_with_selected_polygon(
        layers,
        polygon,
        max_size=(size_x, size_y))
    return utils.serve_pil_image(img)


@app.route('/proteccion/map/<polygon_text>/<int:size_x>x<int:size_y>/tile.png', methods=['GET'])
@crossdomain(origin='*')
def proteccion_map_tile(polygon_text, size_x, size_y):
    try:
        polygon = utils.create_polygon(polygon_text)
    except ValueError:
        abort(404)

    layers = current_app.config['MAP_LAYERS']['proteccion']
    img = maputils.generate_map_with_selected_polygon(
        layers,
        polygon,
        max_size=(size_x, size_y))
    return utils.serve_pil_image(img)


@app.route('/sacosta/pdf/<polygon_text>/sacosta_report.pdf', methods=['GET'])
@crossdomain(origin='*')
def sacosta_pdf_report(polygon_text):
    try:
        polygon = utils.create_polygon(polygon_text)
    except ValueError:
        abort(404)
    pdf = reporting.generate_sacosta_report(current_app.config, polygon)
    return send_file(pdf.name, mimetype='application/pdf')


@app.route('/proteccion/pdf/<polygon_text>/sacosta_report_gradosproteccion.pdf', methods=['GET'])
@crossdomain(origin='*')
def proteccion_pdf_report(polygon_text):
    try:
        polygon = utils.create_polygon(polygon_text)
    except ValueError:
        abort(404)
    pdf = reporting.generate_proteccion_report(current_app.config, polygon)
    return send_file(pdf.name, mimetype='application/pdf')
