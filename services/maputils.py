# -*- coding:utf-8 -*-
from owslib.wms import WebMapService
import pyproj
from PIL import Image
import cStringIO
import urllib
from PIL import ImageDraw


def distance(lat1, lng1, lat2, lng2, ellps='WGS84'):
    """ Distance between two points
    """
    g = pyproj.Geod(ellps=ellps)
    return g.inv(lng1, lat1, lng2, lat2)[2]


def distance_between(p1, p2):
    """ Distance between two points

    :param p1: coordinates of the first point
    :param p2: coordinates of the second point
    :returns: distance
    """
    return distance(p1[0], p1[1], p2[0], p2[1])


def coordinates_to_image_position(bbox, dimensions):
    """ Get function to convert lat,lon coordinates to position in a image
    (relative coordinates inside a image)

    :param bbox: coordinates of the bounding box of the image
    :param dimensions: image dimensions
    :returns: function to convert coordinates to image position
    """
    long_x = bbox[2] - bbox[0]
    long_y = bbox[3] - bbox[1]
    scale_x = dimensions[0] / long_x
    scale_y = -dimensions[1] / long_y
    offset_x = 0
    offset_y = dimensions[1]

    def fun(x, y):
        diff_x = x - bbox[0]
        diff_y = y - bbox[1]
        new_x = diff_x * scale_x + offset_x
        new_y = diff_y * scale_y + offset_y
        return (new_x, new_y)

    return fun


def generate_map_tile(layers, bbox, max_size=(500, 500)):
    """ Generate a image with sacosta layers and with a selected polygon

    :param layers: layer list, ordered from bottom to top
    :param polygon_vertices: list
    :param max_size: desired dimensions for the image.
                     These dimensions are adjusted to preserve map proportion
    :returns: PIL image
    """
    # calculate image dimensions
    dx = distance(bbox[0], bbox[1], bbox[2], bbox[1])
    dy = distance(bbox[0], bbox[1], bbox[0], bbox[3])

    ratio = dx / dy
    desired_ratio = max_size[0] / max_size[1]

    if ratio > desired_ratio:
        sizex = max_size[0]
        sizey = int(round(sizex / ratio))
    else:
        sizey = max_size[1]
        sizex = int(round(sizey * ratio))

    image_dimensions = (sizex, sizey)

    # load images from WMS
    serverurl = 'http://gis.socib.es/geoserver/ows'
    wms = WebMapService(serverurl, version='1.1.1')
    srs = 'EPSG:4326'

    map_img = wms.getmap(layers=layers,
                         srs=srs,
                         bbox=bbox,
                         size=image_dimensions,
                         format='image/png',
                         transparent=True)

    #generate image
    image = Image.open(cStringIO.StringIO(map_img.read()))
    return image


def generate_map_with_selected_polygon(layers, polygon, max_size=(500, 500),
                                       bbox_padding=0.1):
    """ Generate a map image with given layers and a selected polygon

    :param layers: layer list, ordered from bottom to top
    :param polygon: shapely polygon
    :param max_size: desired dimensions for the image.
                     These dimensions are adjusted to preserve map proportion
    :param bbox_padding: extra space that the background image will take from polygon bbox.
                         Expressed in parts per unit of polygon bbox dimensions
    :returns: PIL image
    """
    bounds = polygon.bounds
    # padding relative to bbox dimensions (average of height and width)
    padding = ((bounds[2] + bounds[3] - bounds[0] - bounds[1]) / 2) * bbox_padding
    bbox = (bounds[0] - padding,
            bounds[1] - padding,
            bounds[2] + padding,
            bounds[3] + padding)

    background = generate_map_tile(layers, bbox, max_size)

    # draw polygon
    conv = coordinates_to_image_position(bbox, background.size)
    poly = Image.new('RGBA', background.size)
    pdraw = ImageDraw.Draw(poly)
    pdraw.polygon([conv(float(v[0]), float(v[1])) for v in polygon.exterior.coords],
                  fill=(0, 0, 0, 127), outline=(0, 0, 0, 255))

    # combine with image
    background.paste(poly, mask=poly)

    return background


def get_layer_legend(layer, max_size=(400, 200)):
    """ Return first legend of a layer

    :param layer: layer
    :returns: PIL image
    """
    serverurl = 'http://gis.socib.es/geoserver/ows'
    wms = WebMapService(serverurl, version='1.1.1')
    layer_style = wms[layer].styles.keys()[0]
    legend_url = wms[layer].styles[layer_style]['legend']
    legend = Image.open(cStringIO.StringIO(urllib.urlopen(legend_url).read()))

    # crop legend
    if legend.size[0] > max_size[0] or legend.size[1] > max_size[1]:
        ratio = legend.size[0] / legend.size[1]
        desired_ratio = max_size[0] / max_size[1]

        if ratio > desired_ratio:
            new_sizex = max_size[0]
            new_sizey = int(round(new_sizex / ratio))
        else:
            new_sizey = max_size[1]
            new_sizex = int(round(new_sizey * ratio))

        # legend = legend.resize((new_sizex, new_sizey), Image.ANTIALIAS)
        legend = legend.crop((0, 0, new_sizex, new_sizey))

    return legend
