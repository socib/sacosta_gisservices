# -*- coding:utf-8 -*-

from flask import send_file
from flask import jsonify
import StringIO


def get_polygon_vertices_from_string(polygon):
    """ Get list of vertexs from comma separated values

    :param polygon: string with a list of floats separated by commas that represents polygon vertexs
    :returns: list of vertexs
    """
    polygon = polygon.split(',')

    # Security check. All elements in polygon must be floats
    for coord in polygon:
        try:
            float(coord)
        except ValueError:
            raise ValueError(
                'You must specify a polygon with a list of floats representing its vertices (comma separated)')

    vertices = zip(*[polygon[i::2] for i in range(2)])
    return vertices


def get_makepolygon_from_string(polygon):
    """ Get ST_MakePolygon PostGIS SQL statement from a polygon

    :param polygon: string with a list of floats separated by commas that represents polygon vertexs
    :returns: string
    """
    vertices = get_polygon_vertices_from_string(polygon)

    # close the polygon
    if vertices[0] != vertices[-1]:
        vertices.append(vertices[0])

    polygon_text = 'LINESTRING('
    for vertex in vertices:
        polygon_text += vertex[0] + ' ' + vertex[1] + ' 1, '

    polygon_text = polygon_text[:-2] + ')'
    region = "ST_MakePolygon(ST_GeomFromText('%s',4326))" % polygon_text

    return region


def serve_pil_image(pil_img):
    """ Serve a image from a PIL object

    :param pil_img: image tp serve
    """
    img_io = StringIO.StringIO()
    pil_img.save(img_io, pil_img.format)
    img_io.seek(0)
    mimetype = ''.join(['image/', pil_img.format.lower()])
    return send_file(img_io, mimetype=mimetype)


def send_json_data(data):
    return jsonify({'data': data})


ESICOSTES = {
    "1-A": {
        "color": '#070707',
        "description": 'Costas rocosas altas y acantilados expuestos a la incidencia directa del oleaje'
    },
    "1-B": {
        "color": '#838383',
        "description": 'Estructuras artificiales expuestas a la incidencia directa del oleaje'
    },
    "1-C": {
        "color": '#040404',
        "description": 'Costas rocosas altas con depósitos de derrubios y acumulación de bloques en la base expuestas a la incidencia directa del oleaje'
    },
    "2": {
        "color": '#993300',
        "description": 'Costas rocosas bajas expuestas a la incidencia directa del oleaje'
    },
    "3-A": {
        "color": '#ffff00',
        "description": 'Playas formadas por arenas finas y de grano medio'
    },
    "3-B": {
        "color": '#ffaa01',
        "description": 'Escarpes y costas de perfil escalonado formadas por conglomerados, arenas, limos y arcillas y por litologías calcareníticas'
    },
    "4": {
        "color": '#CFCF6A',
        "description": 'Playas formadas por arenas gruesas'
    },
    "5": {
        "color": '#FFBEBE',
        "description": 'Playas mixtas, formadas por arenas y gravas'
    },
    "6-A": {
        "color": '#FF00C5',
        "description": 'Playas de gravas, cantos rodados y bloques'
    },
    "6-B": {
        "color": '#8405A7',
        "description": 'Costas rocosas bajas expuestas al oleaje, de perfil escalonado y cóncavo con presencia de bloques y/o playas de arenas y cantos'
    },
    "7-A": {
        "color": '#70A600',
        "description": 'Costas rocosas de altura variable en zonas de baja energía'
    },
    "7-B": {
        "color": '#D5FFFF',
        "description": 'Estructuras artificiales localizadas en zonas sin incidencia directa del oleaje'
    },
    "7-C": {
        "color": '#00734C',
        "description": 'Costas rocosas bajas con presencia de bloques y/o playas de arenas y cantos en zonas de baja energía'
    },
    "7-D": {
        "color": '#267301',
        "description": 'Costas rocosas altas con depósitos de derrubios y acumulación de bloques en la base con poca incidencia directa del oleaje'
    },
    "8": {
        "color": '#E60000',
        "description": 'Zonas costeras en contacto o presencia de albuferas y marismas'
    }
}

import re
from unidecode import unidecode

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))


def get_esicostes_description(esicostes):
    if ESICOSTES[esicostes]:
        return ESICOSTES[esicostes]['description'].decode('utf-8')
    else:
        return ''

def get_esicostes_color(esicostes):
    if ESICOSTES[esicostes]:
        return ESICOSTES[esicostes]['color']
    else:
        return ''


def format_longitud(longitud, units='m'):
    if units == 'km':
        return '{0:.2f} km'.format(longitud/1000)
    return '{0:.2f} m'.format(longitud)