# -*- coding:utf-8 -*-

from flask import Blueprint, jsonify, current_app, abort, send_file
from decorators.crossdomain import crossdomain

import utils
import gisdata
import maputils
import reporting

app = Blueprint('services', __name__, template_folder='templates')


@app.route('/api/v1.0/sacosta/<float:xmin>/<float:ymin>/<float:xmax>/<float:ymax>', methods=['GET'])
@crossdomain(origin='*')
def get_sacosta_bbox(xmin, ymin, xmax, ymax):
    region = "ST_MakeEnvelope(%f,%f,%f,%f,4326)" % (xmin, ymin, xmax, ymax)
    return gisdata.get_data_sacosta(current_app.config, region)


@app.route('/api/v1.0/sacosta/<polygon>', methods=['GET'])
@crossdomain(origin='*')
def get_sacosta_polygon(polygon):
    try:
        region = utils.get_makepolygon_from_string(polygon)
    except ValueError, e:
        return jsonify({'error': str(e)})
    return gisdata.get_data_sacosta(current_app.config, region)


@app.route('/api/v1.0/proteccion/<polygon>', methods=['GET'])
@crossdomain(origin='*')
def get_proteccion_polygon(polygon):
    try:
        region = utils.get_makepolygon_from_string(polygon)
    except ValueError, e:
        return jsonify({'error': str(e)})
    return gisdata.get_data_proteccion(current_app.config, region)


@app.route('/api/v1.0/uso-humano/<polygon>', methods=['GET'])
@crossdomain(origin='*')
def get_usohumano_polygon(polygon):
    try:
        region = utils.get_makepolygon_from_string(polygon)
    except ValueError, e:
        return jsonify({'error': e})
    return gisdata.get_data_usohumano(current_app.config, region)


@app.route('/sacosta/map/<polygon>/<int:size_x>x<int:size_y>/tile.png', methods=['GET'])
@crossdomain(origin='*')
def sacosta_map_tile(polygon, size_x, size_y):
    try:
        vertices = utils.get_polygon_vertices_from_string(polygon)
    except ValueError:
        abort(404)

    img = maputils.generate_sacosta_map_with_selected_polygon(vertices, max_size=(size_x, size_y))
    return utils.serve_pil_image(img)


@app.route('/sacosta/pdf/<polygon>/sacosta_report.pdf', methods=['GET'])
@crossdomain(origin='*')
def sacosta_pdf_report(polygon):
    pdf = reporting.generate_sacosta_report(polygon)
    return send_file(pdf.name, mimetype='application/pdf')