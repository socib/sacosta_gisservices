
Introduction
------------

SensibilidadAmbiental is a geoexplorer plugin that provide a tool to draw a polygon on the map and
get information of the environmental sensitivity of the coastline selected. It shows two d3js plots and
links to pdf reports.

Prerequisites
-------------
- `D3.js <http://d3js.org/>`_
- `jQuery <http://jquery.com/>`_

(added to app/templates/composer.html)


Add to Geoexplorer
------------------

Add sacosta_sensibilidadambiental tool at config.tools object in GeoExplorer.Composer (app/static/script/GeoExplorer.js)::

    config.tools = [
        {...},
        {
            ptype: "sacosta_sensibilidadambiental",
            actionTarget: {
                target: "paneltbar",
                index: 18
            }
        }
    ]

