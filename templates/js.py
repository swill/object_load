import re

# graph swift and s3 together
def draw_api_comparison(provider, run, unit, action, max_time, col_width):
    data = {}
    data['provider'] = provider
    data['action'] = action
    data['run'] = run
    data['unit'] = unit
    data['max_time'] = str(max_time)
    data['col_width'] = str(col_width)
    data['el'] = "%s_s3_swift_%s_%s" % (re.sub(r'\W+', '_', provider.lower()), run, action)
    return """
function draw_%(el)s() {
    // Create and populate the data table.
    var data = google.visualization.arrayToDataTable(%(el)s);

    // Create and draw the visualization.
    var ac = new google.visualization.ComboChart(document.getElementById('%(el)s'));
    ac.draw(data, {
        title : 'S3 API vs Swift API %(action)sing %(run)s files',
        width: %(col_width)s,
        height: 300,
        vAxis: {title: 'Time (s)', minValue: 0, maxValue: %(max_time)s, format: '#.#'},
        hAxis: {title: 'File Size (%(unit)s)'},
        seriesType: "bars",
        series: {}
    });
}
google.setOnLoadCallback(draw_%(el)s);
    """ % data


# graph either swift or s3 averages
def draw_api(provider, api, run, unit, action, max_time, col_width):
    data = {}
    data['provider'] = provider
    data['action'] = action
    data['api'] = api.title()
    data['run'] = run
    data['unit'] = unit
    data['max_time'] = str(max_time)
    data['col_width'] = str(col_width)
    data['el'] = "%s_%s_%s_%s" % (re.sub(r'\W+', '_', provider.lower()), api, run, action)
    data['series'] = "series: {}"
    if api == 'swift':
        data['series'] = "series: {0: {color: '#dc3912'}}"
    return """
function draw_%(el)s() {
    // Create and populate the data table.
    var data = google.visualization.arrayToDataTable(%(el)s);
  
    // Create and draw the visualization.
    var ac = new google.visualization.ComboChart(document.getElementById('%(el)s'));
    ac.draw(data, {
        title : '%(api)s API %(action)sing %(run)s files',
        width: %(col_width)s,
        height: 300,
        vAxis: {title: 'Time (s)', minValue: 0, maxValue: %(max_time)s, format: '#.#'},
        hAxis: {title: 'File Size (%(unit)s)'},
        seriesType: "bars",
        %(series)s
    });
}
google.setOnLoadCallback(draw_%(el)s);
    """ % data


# graph either swift or s3 individual runs
def draw_api_run(provider, api, run, unit, action, max_time):
    data = {}
    data['provider'] = provider
    data['api'] = api.title()
    data['run'] = run
    data['unit'] = unit
    data['action'] = action
    data['max_time'] = str(max_time)
    data['el'] = "%s_%s_%s_%s_runs" % (re.sub(r'\W+', '_', provider.lower()), api, run, action)
    data['group'] = ''
    if run == 'small':
        data['group'] = ", bar: {groupWidth: '80%'}"
    return """
function draw_%(el)s() {
    // Create and populate the data table.
    var data = google.visualization.arrayToDataTable(%(el)s);
  
    // Create and draw the visualization.
    var ac = new google.visualization.ComboChart(document.getElementById('%(el)s'));
    ac.draw(data, {
        title : '%(provider)s | %(api)s API %(action)sing %(run)s files',
        width: '100%%',
        height: 400,
        vAxis: {title: 'Time (s)', minValue: 0, maxValue: %(max_time)s},
        hAxis: {title: 'File Size (%(unit)s)'},
        seriesType: "bars",
        series: {}%(group)s
    });
}
google.setOnLoadCallback(draw_%(el)s);
    """ % data



