# -*- coding:utf-8 -*-

from owslib.wms import WebMapService
import pyproj
from PIL import Image
import cStringIO
import urllib
from PIL import ImageDraw



def distance(lat1, lng1, lat2, lng2, ellps = 'WGS84'):
    """ Distance between two points
    """

    g = pyproj.Geod(ellps = ellps)
    return g.inv(lng1, lat1, lng2, lat2)[2]


def distance_between(p1, p2):
    """ Distance between two points

    :param p1: coordinates of the first point
    :param p2: coordinates of the second point
    :returns: distance
    """

    return distance(p1[0], p1[1], p2[0], p2[1])


def coordinates_to_image_position(bbox, dimensions):
    """ Get function to convert lat,lon coordinates to position in a image (relative coordinates inside a image)

    :param bbox: coordinates of the bounding box of the image
    :param dimensions: image dimensions
    :returns: function to convert coordinates to image position
    """

    long_x = bbox[2] - bbox[0]
    long_y = bbox[3] - bbox[1]

    def fun(x, y):
        diff_x = x - bbox[0]
        diff_y = y - bbox[1]
        new_x = diff_x*dimensions[0]/long_x
        new_y = dimensions[1] - diff_y*dimensions[1]/long_y
        return (new_x, new_y)

    return fun


def generate_sacosta_map(bbox, max_size=(500,500)):
    """ Generate a image with sacosta layers and with a selected polygon

    :param polygon_vertices: list
    :param max_size: desired dimensions for the image. These dimensions are adjusted to preserve map proportion
    :returns: PIL image
    """
    # calculate image dimensions
    dx = distance(bbox[0], bbox[1], bbox[2], bbox[1])
    dy = distance(bbox[0], bbox[1], bbox[0], bbox[3])

    ratio = dx/dy
    desired_ratio = max_size[0]/max_size[1]

    if ratio > desired_ratio:
        sizex = max_size[0]
        sizey = int(round(sizex/ratio))
    else:
        sizey = max_size[1]
        sizex = int(round(sizey*ratio))

    image_dimensions = (sizex, sizey)

    # load images from WMS
    serverurl ='http://gis.socib.es/geoserver/ows'
    wms = WebMapService( serverurl, version='1.1.1')
    srs = 'EPSG:4326'

    #let's get the images...
    img_sacosta = wms.getmap( layers=['sa:bal_sa_costa_2012'],
                      srs=srs,
                      bbox=bbox,
                      size=image_dimensions,
                      format='image/png',
                      transparent=True
    )
    img_municip = wms.getmap( layers=['ge:bal_municipios'],
                      srs=srs,
                      bbox=bbox,
                      size=image_dimensions,
                      format='image/png',
                      transparent=True
    )
    img_batimetria = wms.getmap( layers=['batimetria'],
                      srs=srs,
                      bbox=bbox,
                      size=image_dimensions,
                      format='image/png',
                      transparent=True
    )

    #combine images
    background = Image.open(cStringIO.StringIO(urllib.urlopen(img_municip.url).read()))
    layer = Image.open(cStringIO.StringIO(urllib.urlopen(img_batimetria.url).read()))
    background.paste(layer, (0, 0), layer)
    layer = Image.open(cStringIO.StringIO(urllib.urlopen(img_sacosta.url).read()))
    background.paste(layer, (0, 0), layer)

    return background





def generate_sacosta_map_with_selected_polygon(polygon_vertices, max_size=(500,500), bbox_padding=0.01):
    """ Generate a image with sacosta layers and with a selected polygon

    :param polygon_vertices: list
    :param max_size: desired dimensions for the image. These dimensions are adjusted to preserve map proportion
    :param bbox_padding: extra space that the background image will take from polygon bbox
    :returns: PIL image
    """

    bbox = (min([float(v[0]) for v in polygon_vertices]) - bbox_padding,
            min([float(v[1]) for v in polygon_vertices]) - bbox_padding,
            max([float(v[0]) for v in polygon_vertices]) + bbox_padding,
            max([float(v[1]) for v in polygon_vertices]) + bbox_padding)

    background = generate_sacosta_map(bbox, max_size)

    # draw polygon
    conv = coordinates_to_image_position(bbox, background.size)
    poly = Image.new('RGBA', background.size)
    pdraw = ImageDraw.Draw(poly)
    pdraw.polygon([conv(float(v[0]), float(v[1])) for v in polygon_vertices],
                  fill=(0,0,0,127),outline=(0,0,0,255))

    # combine with image
    background.paste(poly, mask=poly)

    return background
