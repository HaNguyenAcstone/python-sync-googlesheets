from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2 import service_account
import os.path
from django.core.files import File

import pymysql
from django.shortcuts import render
import json
# connect database sky007_test
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', database='sky007_test')
cur = db.cursor(pymysql.cursors.DictCursor)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1OR13pTLXY1OZXuPD_ffdDPLxmlQeeEmGX33AibCcUA8'
SAMPLE_RANGE_NAME = 'raw-data!A2:F'

def index(request):
    return render(request,  'index.html', context={ 'text': '123' })

# Create your views here.
@api_view(['GET', 'POST'])
def get_list_post(request):
    if request.method == 'POST':
        databody = json.loads(request.body)
        print(databody['startDate'], databody['endDate'])
        print('start sync data google sheets')

        CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
        f = open(CURRENT_PATH + '\cache.txt', 'r')

        global lastId

        if f.mode == 'r':
            lastId = f.read() or 0

        # query = "SELECT p.id, p.post_date AS 'create_time', pm_bp.meta_value AS 'bill_phone', pm_sfn.meta_value AS 'customer',oim_lt.meta_value AS 'total_price',\
        # GROUP_CONCAT(CONCAT(oi.order_item_name, '- (Qty: ', oim_qty.meta_value, ')') SEPARATOR', ') AS 'list_order'\
        # FROM post AS p JOIN postmeta AS pm_sfn ON p.id = pm_sfn.post_id\
        # JOIN postmeta AS pm_bp ON p.id = pm_bp.post_id\
        # JOIN order_items AS oi ON oi.order_id = p.id\
        # JOIN order_itemmeta AS oim_qty ON oi.order_item_id = oim_qty.order_item_id\
        # JOIN order_itemmeta AS oim_lt ON oi.order_item_id = oim_lt.order_item_id\
        # WHERE pm_sfn.meta_key = '_shipping_first_name' AND oim_qty.meta_key = '_qty' AND oim_lt.meta_key = '_line_total'\
        # AND p.post_status != 'wc-cancelled' AND p.post_status != 'wc-trash' AND oi.order_item_type = 'line_item' AND pm_bp.meta_key = '_billing_phone' AND\
        # GROUP BY p.id"

        query = "SELECT p.id,n.date_time,IF(n.ord_category='0' ,'Customer',IF(n.ord_category='5' ,'Marketing',IF(n.ord_category='7' ,'Wholesaler',IF(n.ord_category='10' ,'ShopeeBbia',IF(n.ord_category='11' ,'ShopeeBbiaMarketing',IF(n.ord_category='13' ,'Missing',IF(n.ord_category='14' ,'Lotte',IF(n.ord_category='15' ,'LotteMarketing',IF(n.ord_category='16','Sendo',IF(n.ord_category='17','SendoMarketing',IF(n.ord_category='18','Eglips',IF(n.ord_category='19','EglipsMarketing',IF(n.ord_category='20','Lazada',IF(n.ord_category='21','LazadaMarketing',IF(n.ord_category='22','EglipsWholesaler',IF(n.ord_category='24','ShopeeEglips',IF(n.ord_category='25','ShopeeEglipsMarketing',IF(n.ord_category='26','LazadaEglips',IF(n.ord_category='27','LazadaEglipsMarketing',IF(n.ord_category='28','Robins',IF(n.ord_category='29','RobinsMarketing',IF(n.ord_category='30','Watsons',IF(n.ord_category='31','WatsonsMarketing',IF(n.ord_category='32','WholesalerActsone',IF(n.ord_category='33','WholesalerJnain',IF(n.ord_category='34','BeautyBox',IF(n.ord_category='35','BeautyBoxMarketing',IF(n.ord_category='36','Tiki',IF(n.ord_category='37','TikiMarketing',IF(n.ord_category='38','ShopeeC2CMarketing',IF(n.ord_category='39','ShopeeC2CMarketing',IF(n.ord_category='40','LazadaC2C',IF(n.ord_category='41','LazadaC2CMarketing',IF(n.ord_category='42','TikiEglips',IF(n.ord_category='43','TikiEglipsMT',IF(n.ord_category='44','Sociolla',IF(n.ord_category='45','SociollaMT',IF(n.ord_category='46','Bbiavn',IF(n.ord_category='47','BbiavnMT',IF(n.ord_category='48','Mixsoon',IF(n.ord_category='49','MixsoonMT',\
IF(n.ord_category='50','Guardian',IF(n.ord_category='51','GuardianMT',IF(n.ord_category='52','Shopee Mixsoon',IF(n.ord_category='53','Shopee Mixsoon MT',IF(n.ord_category='54','Lazada Mixsoon',IF(n.ord_category='55','Lazada Mixsoon MT',IF(n.ord_category='56','Tiki Mixsoon',IF(n.ord_category='57','Tiki Mixsoon MT',IF(n.ord_category='58','Tiktok',IF(n.ord_category='59','Tiktok MT',IF(n.ord_category='60','Tiktok Mixsoon',IF(n.ord_category='61','Tiktok Mixsoon MT','Undefined!'))))))))))))))))))))))))))))))))))))))))))))))))))))) AS `shop_sale` ,\
MAX( CASE WHEN pm.meta_key = '_billing_phone' AND p.ID = pm.post_id THEN pm.meta_value END ) AS `phone_number`,\
MAX( CASE WHEN pm.meta_key = '_shipping_first_name' AND p.ID = pm.post_id THEN pm.meta_value END ) AS `name`,\
MAX( CASE WHEN pm.meta_key = '_order_total' AND p.ID = pm.post_id THEN pm.meta_value END ) AS `total_order`\
FROM  `aowp_posts` p \
LEFT JOIN `aowp_postmeta` pm ON p.id=pm.`post_id`\
LEFT JOIN `tb_ord_note` n ON p.id=n.order_id\
WHERE `date_time` BETWEEN '2023-01-01 00:00:00' AND '2023-12-31 23:59:00'\
AND p.post_status!='trash' AND  p.post_status!='wc-cancelled' \
GROUP BY  p.ID\
ORDER BY  date_time"
        
        result = []
        data = []
        cur.execute(query)

        # map variable cur save data to database
        for row in cur:
            data.append(row)

        if(len(data) == 0):
            print('Nothing Changes')
            return Response({
                'status': 'ok',
                'message': 'Nothing Changes',
                # 'data': result
            })

        # clean data sent google sheets
        for row in data:
            arrTemp = []
            for obj in row:
                if obj == 'create_time':
                    arrTemp.append(row[obj].strftime("%m/%d/%Y %H:%M:%S"))
                else:
                    arrTemp.append(row[obj])
            result.append(arrTemp)

        # sync data to google sheets
        credentials = None
        credentials = service_account.Credentials.from_service_account_file(
            (CURRENT_PATH) + '\credentials.json', scopes=SCOPES)

        service = build('sheets', 'v4', credentials=credentials)

        body={
            "values": result
        }

        sheet = service.spreadsheets()
        resultSync = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME, valueInputOption="USER_ENTERED" 
            , body=body).execute()
        
        print(resultSync)
        #end sync data to google sheets

        lastItem = data[len(data) - 1] # get last item array

        f = open(CURRENT_PATH + '\cache.txt', 'w') # create file with name 'cache.txt' 
        
        # write id last item and total count in database
        cache_file = File(f)
        cache_file.write(str(lastItem['id']))
        cache_file.close
        f.close

        return Response({
            'status': 'ok',
            'message': 'Sync data to google sheets successfully.',
            # 'data': result
        })

