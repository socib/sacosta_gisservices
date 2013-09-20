# -*- coding:utf-8 -*-

from flask import Blueprint, jsonify, current_app
import psycopg2
from decorators.crossdomain import crossdomain


app = Blueprint('services', __name__, template_folder='templates')

# @app.route("/<post_slug>")
# def post_view(post_slug):
#     post = Post.query.filter_by(slug=post_slug).first()
#     return render_template('post.html', post=post)


@app.route('/api/v1.0/sacosta/<float:xmin>/<float:ymin>/<float:xmax>/<float:ymax>', methods = ['GET'])
@crossdomain(origin='*')
def get_sacosta_bbox(xmin, ymin, xmax, ymax):
    region = "ST_MakeEnvelope(%f,%f,%f,%f,4326)" % (xmin, ymin, xmax, ymax)
    return get_result_sacosta(region)


@app.route('/api/v1.0/sacosta/<polygon>', methods = ['GET'])
@crossdomain(origin='*')
def get_sacosta_polygon(polygon):
    polygon = polygon.split(',')

    # Security check. All elements in polygon must be floats
    for coord in polygon:
        try:
            float(coord)
        except ValueError:
            return jsonify({ 'error' : 'You must specify a polygon with a list of floats representing its vertices (comma separated)'})

    vertexs = zip(*[polygon[i::2] for i in range(2)])
    if vertexs[0] != vertexs[-1]:
        vertexs.append(vertexs[0])

    polygon_text = 'LINESTRING('
    for vertex in vertexs:
        polygon_text += vertex[0] + ' ' + vertex[1] + ' 1, '

    polygon_text = polygon_text[:-2] + ')'
    region = "ST_MakePolygon(ST_GeomFromText('%s',4326))" % polygon_text

    return get_result_sacosta(region)



def get_result_sacosta(region):
    conn = psycopg2.connect(current_app.config['DATABASE_URI'])
    cur = conn.cursor()

    strSql = """
    SELECT sci."ESICOSTES", count(1) as num_features, sum("LONGITUD") as longitud,
    sum(st_length(the_geom_intersec)) as longitud_intersec,
    string_agg(sci."HOTLINK", '|') as hotlink
    FROM (
        SELECT sc.*,
        ST_Intersection(
            ST_Transform(%s, 3043),
            the_geom) as the_geom_intersec
        FROM sacosta.bal_sa_costa_2012 as sc
        WHERE ST_Intersects(
            ST_Transform(%s, 3043),
            the_geom)
    ) AS sci
    GROUP BY "ESICOSTES"
    ORDER BY "ESICOSTES"
    """ % (region, region)

    cur.execute(strSql)
    c = cur.fetchall()
    columns = cur.description
    cur.close()

    rows = []
    for i in range(len(c)):
        tmp = {}
        for (index,column) in enumerate(c[i]):
            tmp[columns[index][0]] = column
        rows.append(tmp)

    # Process the result
    result = []
    for row in rows:
        obj = {}
        obj['esicostes'] = row['ESICOSTES']
        if row['hotlink']:
            obj['hotlink'] = [link for link in row['hotlink'].split('|')]
        obj['longitud'] = round(row['longitud_intersec'],2)

        result.append(obj)


    return jsonify({ 'data' : result})