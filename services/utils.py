# -*- coding:utf-8 -*-

from flask import send_file
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

