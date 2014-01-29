# -*- coding:utf-8 -*-

from pyjon.reports import ReportFactory
import tempfile

import utils
import maputils

def generate_sacosta_report(polygon):
    """ Generate a pdf from sacosta data

    :param polygon: string with a list of floats separated by commas that represents polygon vertexs
    :returns: temporary file
    """

    template = 'templates/template_map.xml'

    # generate image
    vertices = utils.get_polygon_vertices_from_string(polygon)
    img = maputils.generate_sacosta_map_with_selected_polygon(vertices, max_size=(400, 400))
    img_tf = tempfile.NamedTemporaryFile(suffix='.png')
    img.save(img_tf)

    factory = ReportFactory()

    factory.render_template(
            template_file=template,
            title='Prova illustration',
            image=img,
            image_filename=img_tf.name)

    tf = tempfile.NamedTemporaryFile()
    factory.render_document(
            tf.name)

    factory.cleanup()

    return tf


