
def build_html(cols, col_width, js, up_cols, up_runs, dn_cols, dn_runs):
    data = {}
    data['col_width'] = str(col_width)
    data['total_width'] = str((cols * col_width * 2) + 24)
    data['section_width'] = str(cols * col_width)
    data['js'] = js
    data['up_cols'] = up_cols
    data['up_runs'] = up_runs
    data['dn_cols'] = dn_cols
    data['dn_runs'] = dn_runs
    return """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>Object Storage Comparison</title>
    <style type="text/css">
    body {
      width:%(total_width)spx;
      font-family: Arial;
      border: 0 none;
    }
    .section {
      width:%(section_width)spx;
      float:left;
    }
    .section-right {
      margin-left:10px;
      border-left:3px solid #eee;
      padding-left:10px;
    }
    .section-title {
      width:100%%;
      font-weight:bold;
      font-size:200%%;
      text-align:center;
      margin-top:10px;
      text-decoration:underline;
    }
    .section-desc {
      width:100%%;
      font-weight:bold;
      font-size:100%%;
      text-align:center;
      margin-top:5px;
      margin-bottom:30px;
    }
    .column-wrapper {
      margin-left:auto;
      margin-right:auto;
    }
    .column {
      width:%(col_width)spx;
      float:left;
    }
    .title {
      font-weight:bold;
      font-size:150%%;
      text-align:center;
      width:100%%;
    }
    .column-graph {
      width: 100%%;
      height: 300px;
    }
    .details {
      clear:both;
    }
    .details-title {
      width:100%%;
      font-weight:bold;
      font-size:190%%;
      text-align:center;
      padding-top:100px;
      text-decoration:underline;
    }
    .details-section {
      padding-top:40px;
    }
    .runs-title {
      width:100%%;
      font-weight:bold;
      font-size:110%%;
      text-align:center;
    }
    .runs-graph {
      width: 100%%;
      height: 400px;
      margin-left:auto;
      margin-right:auto;
    }
    </style>
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1', {packages: ['corechart']});
    </script>
    <script type="text/javascript">
      %(js)s
    </script>
  </head>
  <body>
    <div class="section">
      <div class="section-title">Uploading</div>
      <div class="section-desc">Average Performance</div>
      <div class="column-wrapper">
        %(up_cols)s
      </div>
      <div class="details">
        <div class="details-title">Raw Data</div>
        %(up_runs)s
      </div>
    </div>
    
    <div class="section section-right">
      <div class="section-title">Downloading</div>
      <div class="section-desc">Average Performance</div>
      <div class="column-wrapper">
        %(dn_cols)s
      </div>
      <div class="details">
        <div class="details-title">Raw Data</div>
        %(dn_runs)s
      </div>
    </div>
  </body>
</html>
    """ % (data)