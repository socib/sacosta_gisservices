# -*- coding:utf-8 -*-

import psycopg2
from psycopg2.extras import DictCursor


def get_data_sacosta(config, polygon):
    """ Get aggregated data of coastline sensibility for a given region

    :param config: app config
    :param polygon: shapely polygon
    :returns: array with the result of longitude and images for each type of coast
    """

    region = "ST_GeomFromText('{polygon_text}', 4326)".format(polygon_text=polygon.wkt)

    sql_sacosta = """
    SELECT sci."ESICOSTES", count(1) as num_features, sum("LONGITUD") as longitud,
    sum(st_length(the_geom_intersec)) as longitud_intersec,
    string_agg(sci."HOTLINK", '|') as hotlink
    FROM (
        SELECT sc.*,
        ST_Intersection(
            ST_Transform({region}, 3043),
            the_geom) as the_geom_intersec
        FROM sacosta.bal_sa_costa_2012 as sc
        WHERE ST_Intersects(
            ST_Transform({region}, 3043),
            the_geom)
    ) AS sci
    GROUP BY "ESICOSTES"
    ORDER BY "ESICOSTES"
    """.format(region=region)

    conn = psycopg2.connect(config['DATABASE_URI'])
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(sql_sacosta)
    # Process the result
    result = []
    for row in cur:
        obj = {
            'esicostes': row['ESICOSTES'],
            'longitud': round(row['longitud_intersec'], 2),
            'hotlink': []
        }
        if row['hotlink'] is not None:
            obj['hotlink'] = [link for link in row['hotlink'].split('|')]
        result.append(obj)
    return result


def get_data_proteccion(config, polygon):
    """ Get aggregated data of protection types of a given region

    :param config: app config
    :param polygon: shapely polygon
    :returns: array with data for each type of protection
    """
    region = "ST_GeomFromText('{polygon_text}', 4326)".format(polygon_text=polygon.wkt)

    sql_proteccion = """
    SELECT gpci.proteccion, gpci.ambito, count(1) as num_features,
    string_agg(gpci.toponimia, '|') as toponimia,
    sum(st_area(gpci.the_geom_intersec)) as area_intersec
    from (
        select gpc.*,
            ST_Intersection(
                ST_Transform({region}, 3043),
                the_geom) as the_geom_intersec
        from sacosta.bal_proteccion_2015 gpc
        WHERE ST_isvalid(the_geom) AND ST_Intersects(
            ST_Transform({region}, 3043),
            the_geom)
    ) AS gpci
    GROUP BY proteccion, ambito
    """.format(region=region)

    conn = psycopg2.connect(config['DATABASE_URI'])
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(sql_proteccion)
    # Process the result
    results = {}
    for row in cur:
        # Slip the results for each protection (separated by ;). And each
        # protection, for ambito (terrestre or marino)
        proteccions = row['proteccion']
        if proteccions is None:
            proteccions = '(Ninguna)'
        for proteccio in proteccions.split(';'):
            proteccio = proteccio.strip()

            if not proteccio in results.keys():
                # Init results for this proteccio type
                results[proteccio] = {
                    'proteccion': proteccio,
                    'ambitos': {}
                }
            obj_proteccio = results[proteccio]

            if not row['ambito'] in obj_proteccio['ambitos'].keys():
                # Init results for this proteccio type and ambito
                obj_proteccio['ambitos'][row['ambito']] = {
                    'ambito': row['ambito'],
                    'toponimia': [],
                    'features': [],
                    'num': 0,
                    'area': 0
                }
            obj_ambito = obj_proteccio['ambitos'][row['ambito']]

            if not row['toponimia'] is None:
                obj_ambito['toponimia'].extend(
                    [toponimia for toponimia in row['toponimia'].split('|')])
                obj_ambito['toponimia'] = list(set(obj_ambito['toponimia']))

            obj_ambito['num'] += row['num_features']
            obj_ambito['area'] += row['area_intersec']

    return results


def get_data_usohumano(config, polygon):
    """ Get aggregated data of uso humano for a given region

    :param config: app config
    :param polygon: shapely polygon
    :returns: array with data for each type of protection
    """
    region = "ST_GeomFromText('{polygon_text}', 4326)".format(polygon_text=polygon.wkt)

    sql_usohumano = """
    select uh.*
    from sacosta.bal_uso_humano uh
    WHERE ST_Intersects(
        ST_Transform({region}, 3043),
        the_geom)
    """.format(region=region)

    conn = psycopg2.connect(config['DATABASE_URI'])
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(sql_usohumano)
    # Process the result
    result = []
    for row in cur:
        result.append(row)

    return result
