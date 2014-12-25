#!/usr/bin/env python

import os
import re

# package specific imports
from config import *
from templates.js import *
from templates.html import *

class Parser(object):
    """Parse the log files and build the data to be graphed."""
    def __init__(self, padding=12):
        self.padding = padding
        self.raw_data = {}
        
    def parse(self, api, contents):
        padding = self.padding
        raw_upload = {}
        raw_download = {}
        raw_delete = {}
        for line in contents: # each line
            if len(line) > padding*2 and line[padding*2] == ':': # see if it is an object manipulation
                time = line[0:padding-1].strip()
                size = line[padding:padding*2-1].strip()
                if line[padding*2+1:padding*2+10] == 'uploading': # its an upload op
                    if size in raw_upload:
                        raw_upload[size].append(time)
                    else:
                        raw_upload[size] = [time]
                if line[padding*2+1:padding*2+12] == 'downloading': # its an download op
                    if size in raw_download:
                        raw_download[size].append(time)
                    else:
                        raw_download[size] = [time]
                if line[padding*2+1:padding*2+9] == 'deleting': # its a delete op
                    if size in raw_delete:
                        raw_delete[size].append(time)
                    else:
                        raw_delete[size] = [time]
        if api not in self.raw_data:
            self.raw_data[api] = {}
        self.raw_data[api]['upload'] = raw_upload
        self.raw_data[api]['download'] = raw_download
        self.raw_data[api]['delete'] = raw_delete
            
    def graph_data(self, apis, op='upload', size_unit='KB', output='individual'):
        divisor = 1 # init to a value that is non-destructive
        if size_unit == 'KB':
            divisor = 1024
        if size_unit == 'MB':
            divisor = 1024**2
        if size_unit == 'GB':
            divisor = 1024**3
            
        if 's3' in apis and 'swift' in apis: # provider supports both apis.  compare them.
            graph_data = []
            s3_data = self.raw_data['s3'][op]
            swift_data = self.raw_data['swift'][op]
            keys = [int(x) for x in s3_data.iterkeys()]
            keys.sort()
            keys = [str(x) for x in keys]
            if len(keys) > 0:
                graph_data.append(['File Size ('+size_unit+')', 'S3 API', 'Swift API'])
            for k in keys:
                s3_numbers = [float(v) for v in s3_data[k]]
                swift_numbers = [float(v) for v in swift_data[k]]
                s3_average = sum(s3_numbers) / len(s3_numbers)
                swift_average = sum(swift_numbers) / len(swift_numbers)
                size_in_unit = str(int(k)/divisor)
                graph_data.append([size_in_unit, s3_average, swift_average])
            return graph_data
            
        if 's3' in apis or 'swift' in apis: # provider only supports one api. output results.
            graph_data = []
            data = self.raw_data[apis[0]][op]
            keys = [int(x) for x in data.iterkeys()]
            keys.sort()
            keys = [str(x) for x in keys]
            if len(keys) > 0:
                header = ['File Size ('+size_unit+')']
                if output == 'individual':
                    for index in range(len(data[keys[0]])):
                        header.append('Run '+str(index+1))
                if output == 'average':
                    header.append(apis[0].capitalize()+' API')
                graph_data.append(header)
            for k in keys:
                values = [float(v) for v in data[k]]
                size_in_unit = str(int(k)/divisor)
                if output == 'individual':
                    row = [size_in_unit] + values
                if output == 'average':
                    average = sum(values) / len(values)
                    row = [size_in_unit, average]
                graph_data.append(row)
            return graph_data
                  
if __name__ == "__main__":
    logs_dir = 'logs'
    size_mapping = dict({'small':'KB', 'medium':'MB', 'large':'MB'})
    
    js = ''
    up_cols = ''
    up_runs = {}
    dn_cols = ''
    dn_runs = {}
    up_run_list = []
    dn_run_list = []
    for test_case in test_cases: # number of columns
        provider_code = re.sub(r'\W+', '_', test_case['provider'].lower())
        up_cols = up_cols + '\n' + '<div class="column"><div class="title">%s</div>' % (test_case['provider'])
        dn_cols = dn_cols + '\n' + '<div class="column"><div class="title">%s</div>' % (test_case['provider'])
        for run_obj in test_case['runs']: # rows in columns
            run = run_obj['directory']
            if run in size_mapping:
                if run not in up_runs:
                    up_runs[run] = '<div class="details-section"><div class="runs-title">%s File Runs</div>' % (run.title())
                    if run not in up_run_list:
                        up_run_list.append(run)
                if run not in dn_runs:
                    dn_runs[run] = '<div class="details-section"><div class="runs-title">%s File Runs</div>' % (run.title())
                    if run not in dn_run_list:
                        dn_run_list.append(run)
                parser = Parser()
                for api in test_case['apis']:
                    contents = []
                    try:
                        with open(logs_dir+'/'+provider_code+'_'+api+'_'+run+'.log') as f:
                            contents = f.readlines()
                    except IOError as e:
                        print 'NOTICE: '+logs_dir+'/'+provider_code+'_'+api+'_'+run+'.log does not exist'
                    parser.parse(api, contents)

                # parser now has been populated with the data from the files.
                if len(test_case['apis']) > 1: # compare the different apis on one graph + the runs breakdown for each
                    up_cols = up_cols + '\n' + '<div id="%s_s3_swift_%s_upload" class="column-graph"></div>' % (
                        provider_code, run)
                    dn_cols = dn_cols + '\n' + '<div id="%s_s3_swift_%s_download" class="column-graph"></div>' % (
                        provider_code, run)

                    js = js + '\n' + '//'+test_case['provider']+' '+run # output a JS comment
                    js = js + '\n' + provider_code+'_'+'_'.join(sorted(test_case['apis']))+'_'+run+'_upload = '+repr(parser.graph_data(test_case['apis'], op='upload', size_unit=size_mapping[run]))+';'
                    js = js + '\n' + draw_api_comparison(test_case['provider'], run, size_mapping[run], 'upload', run_obj['max_graph_time'], column_width)
                    js = js + '\n'
                    
                    js = js + '\n' + provider_code+'_'+'_'.join(sorted(test_case['apis']))+'_'+run+'_download = '+repr(parser.graph_data(test_case['apis'], op='download', size_unit=size_mapping[run]))+';'
                    js = js + '\n' + draw_api_comparison(test_case['provider'], run, size_mapping[run], 'download', run_obj['max_graph_time'], column_width)
                    js = js + '\n'
                    
                    for api in sorted(test_case['apis']): # build the runs data
                        up_runs[run] = up_runs[run] + '\n' + '<div id="%s_%s_%s_upload_runs" class="runs-graph"></div>' % (
                            provider_code, api, run)
                        js = js + '\n' + provider_code+'_'+api+'_'+run+'_upload_runs = '+repr(parser.graph_data([api], op='upload', size_unit=size_mapping[run]))+';'
                        js = js + '\n' + draw_api_run(test_case['provider'], api, run, size_mapping[run], 'upload', run_obj['max_graph_time'])
                        js = js + '\n'
                        
                        dn_runs[run] = dn_runs[run] + '\n' + '<div id="%s_%s_%s_download_runs" class="runs-graph"></div>' % (
                            provider_code, api, run)
                        js = js + '\n' + provider_code+'_'+api+'_'+run+'_download_runs = '+repr(parser.graph_data([api], op='download', size_unit=size_mapping[run]))+';'
                        js = js + '\n' + draw_api_run(test_case['provider'], api, run, size_mapping[run], 'download', run_obj['max_graph_time'])
                        js = js + '\n'
                else: # give the average for the specific api on one graph + the runs breakdown for the api
                    up_cols = up_cols + '\n' + '<div id="%s_%s_%s_upload" class="column-graph"></div>' % (
                        provider_code, test_case['apis'][0], run)
                    dn_cols = dn_cols + '\n' + '<div id="%s_%s_%s_download" class="column-graph"></div>' % (
                        provider_code, test_case['apis'][0], run)
                    js = js + '\n' + '//'+test_case['provider']+' '+run # output a JS comment
                    js = js + '\n' + provider_code+'_'+test_case['apis'][0]+'_'+run+'_upload = '+repr(parser.graph_data(test_case['apis'], op='upload', size_unit=size_mapping[run], output='average'))+';'
                    js = js + '\n' + draw_api(test_case['provider'], test_case['apis'][0], run, size_mapping[run], 'upload', run_obj['max_graph_time'], column_width)
                    js = js + '\n'
                    
                    js = js + '\n' + provider_code+'_'+test_case['apis'][0]+'_'+run+'_download = '+repr(parser.graph_data(test_case['apis'], op='download', size_unit=size_mapping[run], output='average'))+';'
                    js = js + '\n' + draw_api(test_case['provider'], test_case['apis'][0], run, size_mapping[run], 'download', run_obj['max_graph_time'], column_width)
                    js = js + '\n'
                    
                    up_runs[run] = up_runs[run] + '\n' + '<div id="%s_%s_%s_upload_runs" class="runs-graph"></div>' % (
                            provider_code, api, run)
                    js = js + '\n' + provider_code+'_'+test_case['apis'][0]+'_'+run+'_upload_runs = '+repr(parser.graph_data(test_case['apis'], op='upload', size_unit=size_mapping[run]))+';'
                    js = js + '\n' + draw_api_run(test_case['provider'], test_case['apis'][0], run, size_mapping[run], 'upload', run_obj['max_graph_time'])
                    js = js + '\n'
                    
                    dn_runs[run] = dn_runs[run] + '\n' + '<div id="%s_%s_%s_download_runs" class="runs-graph"></div>' % (
                            provider_code, api, run)
                    js = js + '\n' + provider_code+'_'+test_case['apis'][0]+'_'+run+'_download_runs = '+repr(parser.graph_data(test_case['apis'], op='download', size_unit=size_mapping[run]))+';'
                    js = js + '\n' + draw_api_run(test_case['provider'], test_case['apis'][0], run, size_mapping[run], 'download', run_obj['max_graph_time'])
                    js = js + '\n'
            else:
                print 'NOTICE: "%s" is not a configured directory' % (run)
        up_cols = up_cols + '\n</div>'
        dn_cols = dn_cols + '\n</div>'

    up_run_html = ''
    for run in up_run_list:
        up_run_html = up_run_html + up_runs[run] + '\n</div>\n'
    
    dn_run_html = ''
    for run in dn_run_list:
        dn_run_html = dn_run_html + dn_runs[run] + '\n</div>\n'

    html = build_html(len(test_cases), column_width, js, up_cols, up_run_html, dn_cols, dn_run_html)

    if not os.path.exists('html'):
        os.makedirs('html')

    with open('html/index.html', 'w') as f:
        f.write(html)

    print '\nOutput saved to: html/index.html\n'
