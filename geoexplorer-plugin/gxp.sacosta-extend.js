// Get Sensibilidad Ambiental from polygon
Ext.namespace("gxp.plugins");
gxp.plugins.SensibilidadAmbiental = Ext.extend(gxp.plugins.Tool, {
    ptype: "sacosta_sensibilidadambiental",
    menuText: "Sensibilidad Ambiental",
    toolTip: "Muestra la sensibilidad ambiental de una área seleccionada",
    mapControls: {
        draw: null,
        drag: null
    },
    polygonLayer: null,
    svg: null,
    svgGP: null,
    reportButton: null,
    dataSA: null,
    dataGP: null,
    //services_host: 'gisservicestest.socib.es',
    services_host: 'localhost:5000',
    esicostes: {
        "1-A": {
            color: '#070707',
            description: 'Costas rocosas altas y acantilados expuestos a la incidencia directa del oleaje'
        },
        "1-B": {
            color: '#838383',
            description: 'Estructuras artificiales expuestas a la incidencia directa del oleaje'
        },
        "1-C": {
            color: '#040404',
            description: 'Costas rocosas altas con depósitos de derrubios y acumulaciçon de bloques en la base expuestas a la incidencia directa del oleaje'
        },
        "2": {
            color: '#993300',
            description: 'Costas rocosas bajas expuestas a la incidencia directa del oleaje'
        },
        "3-A": {
            color: '#ffff00',
            description: 'Playas formadas por arenas finas y de grano medio'
        },
        "3-B": {
            color: '#ffaa01',
            description: 'Escarpes y costas de perfil escalonado formadas por conglomerados, arenas, limos y arcillas y por litologías calcareníticas'
        },
        "4": {
            color: '#CFCF6A',
            description: 'Playas formadas por arenas gruesas'
        },
        "5": {
            color: '#FFBEBE',
            description: 'Playas mixtas, formadas por arenas y gravas'
        },
        "6-A": {
            color: '#FF00C5',
            description: 'Playas de gravas, cantos rodados y bloques'
        },
        "6-B": {
            color: '#8405A7',
            description: 'Costas rocosas bajas expuestas al oleaje, de perfil escalonado y cóncavo con presencia de bloques y/o playas de arenas y cantos'
        },
        "7-A": {
            color: '#70A600',
            description: 'Costas rocosas de altura variable en zonas de baja energía'
        },
        "7-B": {
            color: '#D5FFFF',
            description: 'Estructuras artificiales localizadas en zonas sin incidencia directa del oleaje'
        },
        "7-C": {
            color: '#00734C',
            description: 'Costas rocosas bajas con presencia de bloques y/o playas de arenas y cantos en zonas de baja energía'
        },
        "7-D": {
            color: '#267301',
            description: 'Costas rocosas altas con depósitos de derrubios y acumulación de bloques en la base con poca incidencia directa del oleaje'
        },
        "8": {
            color: '#E60000',
            description: 'Zonas costeras en contacto o presencia de albuferas y marismas'
        }
    },
    constructor: function(config) {
        gxp.plugins.SensibilidadAmbiental.superclass.constructor.apply(this, arguments);
    },
    addActions: function() {
        var actions = gxp.plugins.SensibilidadAmbiental.superclass.addActions.apply(this, [{
            menuText: this.menuText,
            iconCls: "sacosta-icon-sensibilidadambiental",
            disabled: false,
            enableToggle: true,
            tooltip: this.toolTip,
            handler: function() {
                this.drawPolygon();
            },
            scope: this,
            toggleHandler: function(something, state) {
                if (!state) {
                    if (this.mapControls['draw'])
                        this.mapControls['draw'].deactivate();
                    if (this.mapControls['drag'])
                        this.mapControls['drag'].deactivate();
                    // delete previous features
                    if (this.polygonLayer) {
                        this.polygonLayer.removeAllFeatures();
                    }
                    $('.d3plot').hide();
                    // show chart
                    if (this.svg)
                        this.svg
                            .transition()
                            .duration(500)
                            .style("opacity", 0);
                    // show chart
                    if (this.svgGP)
                        this.svgGP
                            .transition()
                            .duration(500)
                            .style("opacity", 0);



                } else {
                    if (this.mapControls['draw']) {
                        this.mapControls['draw'].activate();
                    }

                    // show chart
                    if (this.svg)
                        this.svg
                            .transition()
                            .duration(500)
                            .style("opacity", 1);
                    if (this.svgGP)
                        this.svgGP
                            .transition()
                            .duration(500)
                            .style("opacity", 1);
                    // this.plotSensibilidadAmbientalInfo([]);
                    $('.d3plot').show();

                }
            }
        }]);
        return actions;
    },
    drawPolygon: function() {
        if (!this.polygonLayer) {
            this.polygonLayer = new OpenLayers.Layer.Vector("Polygon selection Layer", {
                styleMap: new OpenLayers.StyleMap({
                    fillColor: "#222222",
                    fillOpacity: 0.4,
                    pointRadius: 2,
                    strokeColor: "#444444",
                    strokeWidth: 5,
                    strokeOpacity: 0.9
                })
            });
            this.target.mapPanel.map.addLayer(this.polygonLayer);
        }
        if (!this.mapControls['draw']) {
            this.mapControls['draw'] = new OpenLayers.Control.DrawFeature(this.polygonLayer, OpenLayers.Handler.Polygon, {
                'displayClass': 'olControlDrawFeaturePolygon',
                'featureAdded': OpenLayers.Function.bind(this.onFinishDrawPolygon, this)
            });
            this.target.mapPanel.map.addControl(this.mapControls['draw']);
            this.mapControls['draw'].activate();
        }
    },
    onFinishDrawPolygon: function() {
        this.mapControls['draw'].deactivate();
        if (!this.mapControls['drag']) {
            this.mapControls['drag'] = new OpenLayers.Control.DragFeature(this.polygonLayer, {
                'onComplete': OpenLayers.Function.bind(this.getSensibilidadAmbientalInfo, this)
                //'onDrag': OpenLayers.Function.bind(this.getSensibilidadAmbientalInfo, this)
            });
            this.target.mapPanel.map.addControl(this.mapControls['drag']);
        }
        this.mapControls['drag'].activate();
        this.getSensibilidadAmbientalInfo();
    },
    getPolygonWKT: function(){
        var wkt_formater = new OpenLayers.Format.WKT({
            'internalProjection': this.target.mapPanel.map.getProjectionObject(),
            'externalProjection': new OpenLayers.Projection("EPSG:4326")
        });
        return wkt_formater.write(this.polygonLayer.features[0]);
    },
    getSensibilidadAmbientalInfo: function() {
        var polygon_wkt = this.getPolygonWKT();

        $.getJSON('http://' + this.services_host + '/api/v1.0/sacosta/' + polygon_wkt, (function(jsondata) {
            if (jsondata.data) {
                this.plotSensibilidadAmbientalInfo(jsondata.data);
            } else {
                console.log('Error retreiving data from gisservices ' + jsondata.error || '');
            }
        }).bind(this));

        $.getJSON('http://' + this.services_host + '/api/v1.0/proteccion/' + polygon_wkt, (function(jsondata) {
            if (jsondata.data) {
                this.plotGradosProteccionInfo(jsondata.data);
            } else {
                console.log('Error retreiving data from gisservices ' + jsondata.error || '');
            }
        }).bind(this));

    },
    plotSensibilidadAmbientalInfo: function(data) {
        var keys = d3.keys(this.esicostes);
        for (var i = 0, l = keys.length; i < l; i++) {
            // Look up this esicostes inside data. If it doesn't exist, add with 0.
            var esicostesFound = false;
            for (var id = 0, ld = data.length; id < ld; id++) {
                if (keys[i] == data[id].esicostes) {
                    esicostesFound = true;
                    break;
                }
            }
            if (!esicostesFound) {
                data.push({
                    'esicostes': keys[i],
                    'hotlink': '',
                    'longitud': 0
                });
            }

        }

        var map_height = this.target.mapPanel.map.getSize().h;

        var margin = {
            top: 40,
            right: 20,
            bottom: 30,
            left: 90
        },
            height = Math.floor(map_height*0.38) - margin.top - margin.bottom,
            width = Math.floor(map_height*0.55) - margin.left - margin.right;


        var x = d3.scale.ordinal()
            .rangeRoundBands([0, width], 0.1);

        var y = d3.scale.linear()
            .range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .tickFormat(function(d) {
                if ((d / 1000) >= 1) {
                    d = d / 1000 + " Km";
                }else{
                    d = d + " m";
                }
                return d;
            })
            .orient("left");

        // data = data.sort(function(a, b){ return a.esicostes < b.esicostes;});
        data.sort(function(a, b) {
            return (a.esicostes < b.esicostes) ? -1 : 1;
        });
        this.dataSA = data; // save data to use in events

        // x.domain(data.map(function(d) { return d.esicostes; }).sort(function (a,b){return a.esicostes < b.esicostes;}));
        x.domain(keys.sort());
        y.domain([0, d3.max(data, function(d) {
            return d.longitud;
        })]);

        if (!this.svg) {
            this.divContainer = d3.select("body")
                .append("div")
                .attr("class", 'd3plot plot_sensibilidadambiental')
                .attr("style", 'z-index: 0; position: absolute; bottom: 60px; right: 0;');

            this.svg = this.divContainer.append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var div = d3.select("body").append("div")
                .attr("class", "d3tooltip")
                .style("opacity", 0);

            this.svg.append("g")
                .attr("class", "xaxis axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            this.svg.append("g")
                .attr("class", "yaxis axis")
                .call(yAxis);

            this.svg.append("text")
                .attr("x", (width / 2))
                .attr("y", 0 - (margin.top / 2))
                .attr("text-anchor", "middle")
                .style("font-size", "14px")
                .style("font-weight", "bold")
                .text("Sensibilidad ambiental de la costa");

            this.svg.append("svg:line")
                .attr("x1", 20)
                .attr("y1", 0 - (margin.top / 2) + 10)
                .attr("x2", width - 20)
                .attr("y2", 0 - (margin.top / 2) + 10)
                .style("stroke", "rgb(0,0,0)");

            this.svg.append("text")
                .attr("x", 30)
                .attr("y", 0 - (margin.top / 2) + 25)
                .style("font-size", "14px")
                .style("font-weight", "bold")
                .text("-");

            this.svg.append("text")
                .attr("x", width - 35)
                .attr("y", 0 - (margin.top / 2) + 25)
                .style("font-size", "14px")
                .style("font-weight", "bold")
                .text("+");

            this.svg.selectAll("rect")
                .data(data)
                .enter().append("rect")
                .attr("fill", this.getColorBar.bind(this))
                .attr("x", function(d) {
                    return x(d.esicostes);
                })
                .attr("width", x.rangeBand())
                .attr("y", function(d) {
                    return y(d.longitud);
                })
                .attr("height", function(d) {
                    return height - y(d.longitud);
                });

            url_pdf = 'http://' + this.services_host +'/sacosta/pdf/' + this.getPolygonWKT() + '/sacosta_report.pdf';
            this.divContainer.append("a")
                .attr("x", width - 70)
                .attr("y", height - 5)
                .attr('href', url_pdf)
                .attr('target', '_blank')
                .attr('class', 'pdf-report')
                .attr('title', 'Generar informe PDF')
                .attr('title', 'Generar informe PDF')
                .html("Informe PDF");

        } else {
            // update
            /* this.svg.select(".xaxis")
            .transition()
            .duration(100)
            .call(xAxis);

        */

            this.svg.select(".yaxis")
                .transition()
                .duration(100)
                .call(yAxis);

            this.svg.selectAll("rect")
                .data(data)
                .transition()
                .duration(1000)
                .attr("fill", this.getColorBar.bind(this))
                .attr("x", function(d) {
                    return x(d.esicostes);
                })
                .attr("width", x.rangeBand())
                .attr("y", function(d) {
                    return y(d.longitud);
                })
                .attr("height", function(d) {
                    return height - y(d.longitud);
                });

            url_pdf = 'http://' + this.services_host + '/sacosta/pdf/' + this.getPolygonWKT() + '/sacosta_report.pdf';
            this.divContainer.select("a.pdf-report")
                .attr('href', url_pdf);
        }



        this.svg.selectAll("rect")
            .on("click", this.onClickBar.bind(this))
            .on("mouseover", this.onMouseOverBar.bind(this))
            .on("mouseout", this.onMouseOutBar.bind(this));
    },
    getColorBar: function(d) {
        return this.esicostes[d.esicostes].color;
    },
    onClickBar: function(d) {
        console.log(d);

        html = '<h1>Tipo de sensibilidad ambiental de la costa: ' + d.esicostes + ": " + this.esicostes[d.esicostes].description + '</h1><br/><p><b>Longitud:</b> ' + numeral(d.longitud).format('0,0') + " m</b></p><br/><b>Fotografías:</b></br>";

        for (var i = 0, l = d.hotlink.length; i < l; i++) {
            html += '<div class="imatge-sa"><img width="300" height="235" src="http://gis.socib.es/images' + d.hotlink[i] + '" /></div>';
        }
        var lastWindowPosition = null;
        var currentWindow = Ext.WindowMgr.getActive();
        if (currentWindow) {
            lastWindowPosition = currentWindow.getPosition();
        }

        winPanel = new Ext.Window({
            title: 'Sensibilidad Ambiental ' + d.esicostes,
            autoHeight: false,
            height: 350,
            width: 350,
            autoScroll: true,
            html: html
        });
        //winPanel = new Ext.Window({title: 'Feature Info',autoHeight: true,width:300,html: response.responseText});
        winPanel.show();
        if (lastWindowPosition) {
            if (lastWindowPosition[0] + 350 < $(window).width()) {
                winPanel.setPosition([lastWindowPosition[0] + 350, lastWindowPosition[1]]);
            } else {
                winPanel.setPosition([300, lastWindowPosition[1] + 50]);
            }
        }


    },
    onMouseOverBar: function(d, i) {
        d3.select(".d3tooltip")
            .transition()
            .duration(200)
            .style("opacity", 0.9);
        d3.select(".d3tooltip")
            .html(this.getHtlmBar.bind(this, d))
            .style("left", (d3.event.pageX - 330) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
        //this.drawFeatures(d);
        this.redrawLayer(d);
    },
    onMouseOutBar: function(d, i) {
        d3.select(".d3tooltip")
            .transition()
            .duration(500)
            .style("opacity", 0);
        this.redrawLayer(d, false);
    },
    getHtlmBar: function(d) {
        return d.esicostes + ": " + this.esicostes[d.esicostes].description + '<br /> Longitud: <b>' + numeral(d.longitud).format('0,0') + " m</b>";
    },
    plotGradosProteccionInfo: function(data) {

        this.dataGP = $.map(data, function(value, index) {
            value.ambitos = $.map(value.ambitos, function(ambito, index) {
                ambito.area = ambito.area / 1000;
                return [ambito];
            });
            return [value];
        });

        var ambitos = [];
        for (var i = 0, l = this.dataGP.length; i < l; i++) {
            for (var j = 0, lj = this.dataGP[i].ambitos.length; j < lj; j++) {
                this.dataGP[i].ambitos[j].proteccion = this.dataGP[i].proteccion;
                ambitos.push(this.dataGP[i].ambitos[j]);
            }
        }


        //this.dataGP = data;
        var map_height = this.target.mapPanel.map.getSize().h;

        var margin = {
            top: 40,
            right: 20,
            bottom: 30,
            left: 90
        },
            height = Math.floor(map_height*0.38) - margin.top - margin.bottom,
            width = Math.floor(map_height*0.55) - margin.left - margin.right;

        var x = d3.scale.linear()
            .range([width/10, width]);

        var y = d3.scale.ordinal()
            .rangeBands([0, height], 0.1);

        /*var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");*/

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var keys = d3.keys(data);
        y.domain(keys.sort());
        var max = d3.max(ambitos, function(d) {
            return d.area;
        });
        x.domain([0, max]);

        if (this.svgGP) {
            this.svgGP.remove();
            d3.select(".plot_gradosproteccion").remove();
        }

        var divContainer = d3.select("body")
            .append("div")
            .attr("class", 'd3plot plot_gradosproteccion')
            .attr("style", 'z-index: 0; position: absolute; bottom: ' + (height+170) + 'px; right: 0;');

        this.svgGP = divContainer.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        /*this.svgGP.append("g")
            .attr("class", "xaxis axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);*/

        this.svgGP.append("g")
            .attr("class", "yaxis axis")
            .call(yAxis);

        this.svgGP.append("text")
            .attr("x", (width / 2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .style("font-weight", "bold")
            .text("Grados protección de la costa");

        /*this.svgGP.append("text")
            .attr("x", (width / 2))
            .attr("y", height + margin.bottom)
            .style("font-size", "12px")
            .text("ha");*/


        this.svgGP.selectAll("rect")
            .data(ambitos)
            .enter().append("rect")
            .attr("fill", function(d) {
                if (d.ambito == 'marino')
                    return 'steelblue';
                else
                    return '#843c39';
            })
            .attr("x", 0)
            .attr("y", function(d) {
                var offset = 0;
                if (d.ambito == 'marino')
                    offset = y.rangeBand() / 2;
                return y(d.proteccion) + offset;
            })
            .attr("width", function(d) {
                return x(d.area);
            })
            .attr("height", y.rangeBand() / 2);


        url_pdf = 'http://' + this.services_host + '/proteccion/pdf/' + this.getPolygonWKT() + '/sacosta_report_gradosproteccion.pdf';
        divContainer.append("a")
            .attr("x", width - 70)
            .attr("y", height - 5)
            .attr('href', url_pdf)
            .attr('target', '_blank')
            .attr('class', 'pdf-report')
            .attr('title', 'Generar informe PDF')
            .html("Informe PDF");

        this.svgGP.selectAll("rect")
            .on("click", this.onClickBarGP.bind(this))
            .on("mouseover", this.onMouseOverBarGP.bind(this))
            .on("mouseout", this.onMouseOutBar.bind(this));


    },
    onClickBarGP: function(d) {

        html = '<h1>Grado de protección:' + d.proteccion + ' (ámbito ' + d.ambito + ')</h1><br/><p><b>Núm. zonas:</b> ' + d.num + "</p>";

        html += '<br/><h2>Toponímia:</h2><ul>';
        for (var i = 0, l = d.toponimia.length; i < l; i++) {
            html += '<li>' + d.toponimia[i] + '</li>';
        }
        html += '</ul>';
        var lastWindowPosition = null;
        var currentWindow = Ext.WindowMgr.getActive();
        if (currentWindow) {
            lastWindowPosition = currentWindow.getPosition();
        }

        winPanel = new Ext.Window({
            title: 'Protección de la costa: ' + d.proteccion,
            autoHeight: false,
            height: 350,
            width: 350,
            autoScroll: true,
            html: html
        });
        //winPanel = new Ext.Window({title: 'Feature Info',autoHeight: true,width:300,html: response.responseText});
        winPanel.show();
        if (lastWindowPosition) {
            if (lastWindowPosition[0] + 350 < $(window).width()) {
                winPanel.setPosition([lastWindowPosition[0] + 350, lastWindowPosition[1]]);
            } else {
                winPanel.setPosition([300, lastWindowPosition[1] + 50]);
            }
        }
    },
    onMouseOverBarGP: function(d, i) {
        d3.select(".d3tooltip")
            .transition()
            .duration(200)
            .style("z-index", 100)
            .style("opacity", 1);
        d3.select(".d3tooltip")
            .html(this.getHtlmBarGP.bind(this, d))
            .style("left", (d3.event.pageX - 330) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
        /* this.drawFeatures(d);*/
        this.redrawLayer(d);

    },
    getHtlmBarGP: function(d) {
        var tooltip = '<h1>' + d.proteccion + ' (ámbito ' + d.ambito + ')</h1>Núm. zonas: <b>' + d.num + "</b><br />";
        tooltip += d.toponimia.join(' | ');
        return tooltip;
    },
    redrawLayer: function(d, filter) {
        filter = typeof filter !== 'undefined' ? filter : true;
        var layer, ol_filter;
        if (d.esicostes) {
            layer = this.target.mapPanel.map.getLayersByName("2012 - Sensibilidad ambiental de la costa")[0];
            this.target.mapPanel.map.getLayersByName("Grados de protección de la costa (Mallorca)")[0].setVisibility(false);

            ol_filter = new OpenLayers.Filter.Logical({
                type: OpenLayers.Filter.Logical.AND,
                filters: [
                    new OpenLayers.Filter.Comparison({
                        type: OpenLayers.Filter.Comparison.EQUAL_TO,
                        property: "ESICOSTES",
                        value: d.esicostes
                    })
                    /*, new OpenLayers.Filter.Spatial({
                type: OpenLayers.Filter.Spatial.INTERSECTS,
                value: this.polygonLayer.features[0].geometry,
                projection: "EPSG:900913"
            })
            */
                ]
            });
        } else if (d.proteccion) {
            layer = this.target.mapPanel.map.getLayersByName("Grados de protección de la costa (Mallorca)")[0];
            this.target.mapPanel.map.getLayersByName("2012 - Sensibilidad ambiental de la costa")[0].setVisibility(false);

            if (d.proteccion == '(Ninguna)') {
                    ol_filter = new OpenLayers.Filter.Logical({
                        type: OpenLayers.Filter.Logical.AND,
                        filters: [
                            new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "figuras_proteccion",
                                value: 0
                            }),
                            new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "ambito",
                                value: d.ambito
                            })
                        ]
                    });
                } else {
                    ol_filter = new OpenLayers.Filter.Logical({
                        type: OpenLayers.Filter.Logical.AND,
                        filters: [
                            new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.LIKE,
                                property: "proteccion",
                                value: '*' + d.proteccion + '*'
                            }),
                            new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: "ambito",
                                value: d.ambito
                            })
                        ]
                    });
                }
            } else {
                return;
            }

            if (filter) {
                var filter_1_0 = new OpenLayers.Format.Filter({
                    version: "1.0.0"
                });
                var xml = new OpenLayers.Format.XML();
                var new_filter = xml.write(filter_1_0.write(ol_filter));
                layer.params['FILTER'] = new_filter;
                if (!layer.visibility)
                    layer.setVisibility(true);
            } else {
                layer.params['FILTER'] = null;
            }

            layer.redraw();
        },
        drawFeatures: function(d) {
            if (!d.features)
                return;

            if (this.features_layer) {
                this.features_layer.destroy();
            }
            var layer_title;
            if (d.proteccion)
                layer_title = "Protección: " + d.proteccion + '(' + d.ambito + ')';
            else
                layer_title = "Sensibilidad Ambiental: " + d.esicostes + ": " + this.esicostes[d.esicostes].description;

            var color = '#2a37ff';
            this.features_layer = new OpenLayers.Layer.Vector(layer_title, {
                styleMap: new OpenLayers.StyleMap({
                    fillColor: color,
                    fillOpacity: 0.4,
                    pointRadius: 2,
                    strokeColor: color,
                    strokeWidth: 5,
                    strokeOpacity: 0.9
                })
            });
            this.target.mapPanel.map.addLayer(this.features_layer);

            var geojson_format = new OpenLayers.Format.GeoJSON();
            var geojson = this.postGISQueryToFeatureCollection(d.features);
            this.features_layer.addFeatures(geojson_format.read(JSON.stringify(geojson)));
        },

        postGISQueryToFeatureCollection: function(features) {
            // from https://gist.github.com/samgiles/2299524
            // Initalise variables.
            var i = 0,
                length = features.length,
                prop = null,
                geojson = {
                    "type": "FeatureCollection",
                    "features": []
                }; // Set up the initial GeoJSON object.

            if (length > 2)
                length = 2;
            for (i = 0; i < length; i++) { // For each result create a feature
                var feature = {
                    "type": "Feature",
                    "geometry": features[i]
                };
                // Push the feature into the features array in the geojson object.
                geojson.features.push(feature);
            }
            // return the FeatureCollection geojson object.
            return geojson;
        },

        showReportRegion: function() {
            var map = this.target.mapPanel.map;
            map.div.style.height = '350px';
            map.div.style.width = '350px';
            // map.div.parentElement.style.marginTop = '40px';
            // map.div.parentElement.style.marginLeft = '40px';
            map.updateSize();
            map.zoomToExtent(this.polygonLayer.getDataExtent());

            // Create new div.
            var divReport = $("<div class='sacosta-report-region'></div>");
            // SAmbiental
            var html = '<h1>Sensibilidad Ambiental de la costa</h1>';
            for (var i = 0, l = this.dataSA.length; i < l; i++) {
                html += this.getHTMLInfoSA(this.dataSA[i]);
            }
            divReport.append($(map.div).html());
            divReport.append(html);

            map.div.style.height = '100%';
            map.div.style.width = '100%';
            map.updateSize();

            var w = window.open();
            $(w.document.body).html(divReport);

        },
        getHTMLInfoSA: function(d) {
            var html = '<h1>' + d.esicostes + ": " + this.esicostes[d.esicostes].description + '</h1><p>Longitud: <b>' + numeral(d.longitud).format('0,0') + " m</b></p>";

            for (var i = 0, l = d.hotlink.length; i < l; i++) {
                html += '<div class="imatge-sa"><img width="300" height="235" src="http://gis.socib.es/images' + d.hotlink[i] + '" /></div>';
            }
            return html;
        }
    });
Ext.preg(gxp.plugins.SensibilidadAmbiental.prototype.ptype, gxp.plugins.SensibilidadAmbiental);