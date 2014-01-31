# -*- coding:utf-8 -*-

from pyjon.reports import ReportFactory
import tempfile

import utils
import maputils
import gisdata

def generate_sacosta_report(config, polygon):
    """ Generate a pdf from sacosta data

    :param config: app config
    :param polygon: string with a list of floats separated by commas that represents polygon vertexs
    :returns: temporary file
    """

    template = 'templates/pdf_template_sacosta.xml'

    # generate image
    vertices = utils.get_polygon_vertices_from_string(polygon)
    layers = config['MAP_LAYERS']['sacosta']
    img = maputils.generate_map_with_selected_polygon(layers, vertices, max_size=(400, 300))
    img_tf = tempfile.NamedTemporaryFile(suffix='.png')
    img.save(img_tf)

    # get regionrep
    region = utils.get_makepolygon_from_string(polygon)
    data_sacosta = gisdata.get_data_sacosta(config, region)

    units = 'm'
    if data_sacosta:
        max_longitud = max([tc['longitud'] for tc in data_sacosta])
        if max_longitud > 1000:
            units = 'km'

    factory = ReportFactory()

    factory.render_template(
            template_file=template,
            map=img,
            map_filename=img_tf.name,
            data_sacosta=data_sacosta,
            units_longitud=units)

    tf = tempfile.NamedTemporaryFile()
    factory.render_document(
            tf.name)

    factory.cleanup()

    return tf


def generate_proteccion_report(config, polygon):
    """ Generate a pdf from grados de proteccion data

    :param config: app config
    :param polygon: string with a list of floats separated by commas that represents polygon vertexs
    :returns: temporary file
    """

    template = 'templates/pdf_template_proteccion.xml'

    # generate image
    vertices = utils.get_polygon_vertices_from_string(polygon)
    layers = config['MAP_LAYERS']['proteccion']
    img = maputils.generate_map_with_selected_polygon(layers, vertices, max_size=(400, 300))
    img_tf = tempfile.NamedTemporaryFile(suffix='.png')
    img.save(img_tf)

    # get sacosta legend (changed. No legend, the colors will be shown at the table)
    img_proteccion_legend = maputils.get_layer_legend(layers[-1],max_size=(470, 400))
    img_proteccion_legend_tf = tempfile.NamedTemporaryFile(suffix='.png')
    img_proteccion_legend.save(img_proteccion_legend_tf)


    # get regionrep
    region = utils.get_makepolygon_from_string(polygon)
    data = gisdata.get_data_proteccion(config, region)

    factory = ReportFactory()

    factory.render_template(
            template_file=template,
            map=img,
            map_filename=img_tf.name,
            legend=img_proteccion_legend,
            legend_filename=img_proteccion_legend_tf.name,
            data=data)

    tf = tempfile.NamedTemporaryFile()
    factory.render_document(
            tf.name)

    factory.cleanup()

    return tf


