from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from googleapiclient.discovery import build
from google.oauth2 import service_account
import os.path

import pymysql
from django.shortcuts import render
import json


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1OR13pTLXY1OZXuPD_ffdDPLxmlQeeEmGX33AibCcUA8'
SAMPLE_RANGE_NAME = 'raw-data!A2:F'

def index(request):
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
    print(CURRENT_PATH)
    return render(request,  'index.html', { 'static': CURRENT_PATH})

# Create your views here.
@api_view(['GET', 'POST'])
def get_list_post(request):
    if request.method == 'POST':
        databody = json.loads(request.body)
        print(databody['startDate'], databody['endDate'])
        print('start sync data google sheets')

        CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

        query = "SELECT p.id,n.date_time as create_time,IF(n.ord_category='0' ,'Customer',IF(n.ord_category='5' ,'Marketing',IF(n.ord_category='7' ,'Wholesaler',IF(n.ord_category='10' ,'ShopeeBbia',IF(n.ord_category='11' ,'ShopeeBbiaMarketing',IF(n.ord_category='13' ,'Missing',IF(n.ord_category='14' ,'Lotte',IF(n.ord_category='15' ,'LotteMarketing',IF(n.ord_category='16','Sendo',IF(n.ord_category='17','SendoMarketing',IF(n.ord_category='18','Eglips',IF(n.ord_category='19','EglipsMarketing',IF(n.ord_category='20','Lazada',IF(n.ord_category='21','LazadaMarketing',IF(n.ord_category='22','EglipsWholesaler',IF(n.ord_category='24','ShopeeEglips',IF(n.ord_category='25','ShopeeEglipsMarketing',IF(n.ord_category='26','LazadaEglips',IF(n.ord_category='27','LazadaEglipsMarketing',IF(n.ord_category='28','Robins',IF(n.ord_category='29','RobinsMarketing',IF(n.ord_category='30','Watsons',IF(n.ord_category='31','WatsonsMarketing',IF(n.ord_category='32','WholesalerActsone',IF(n.ord_category='33','WholesalerJnain',IF(n.ord_category='34','BeautyBox',IF(n.ord_category='35','BeautyBoxMarketing',IF(n.ord_category='36','Tiki',IF(n.ord_category='37','TikiMarketing',IF(n.ord_category='38','ShopeeC2CMarketing',IF(n.ord_category='39','ShopeeC2CMarketing',IF(n.ord_category='40','LazadaC2C',IF(n.ord_category='41','LazadaC2CMarketing',IF(n.ord_category='42','TikiEglips',IF(n.ord_category='43','TikiEglipsMT',IF(n.ord_category='44','Sociolla',IF(n.ord_category='45','SociollaMT',IF(n.ord_category='46','Bbiavn',IF(n.ord_category='47','BbiavnMT',IF(n.ord_category='48','Mixsoon',IF(n.ord_category='49','MixsoonMT',\
        IF(n.ord_category='50','Guardian',IF(n.ord_category='51','GuardianMT',IF(n.ord_category='52','Shopee Mixsoon',IF(n.ord_category='53','Shopee Mixsoon MT',IF(n.ord_category='54','Lazada Mixsoon',IF(n.ord_category='55','Lazada Mixsoon MT',IF(n.ord_category='56','Tiki Mixsoon',IF(n.ord_category='57','Tiki Mixsoon MT',IF(n.ord_category='58','Tiktok',IF(n.ord_category='59','Tiktok MT',IF(n.ord_category='60','Tiktok Mixsoon',IF(n.ord_category='61','Tiktok Mixsoon MT','Undefined!'))))))))))))))))))))))))))))))))))))))))))))))))))))) AS `shop_sale` ,\
        MAX( CASE WHEN pm.meta_key = '_billing_phone' AND p.ID = pm.post_id THEN pm.meta_value END ) AS `phone_number`,\
        MAX( CASE WHEN pm.meta_key = '_shipping_first_name' AND p.ID = pm.post_id THEN pm.meta_value END ) AS `name`,\
        MAX( CASE WHEN pm.meta_key = '_order_total' AND p.ID = pm.post_id THEN pm.meta_value END ) AS `total_order`\
        FROM  `aowp_posts` p \
        LEFT JOIN `aowp_postmeta` pm ON p.id=pm.`post_id`\
        LEFT JOIN `tb_ord_note` n ON p.id=n.order_id\
        WHERE `date_time` BETWEEN %s AND %s\
        AND p.post_status!='trash' AND  p.post_status!='wc-cancelled' \
        GROUP BY  p.ID\
        ORDER BY  date_time"
        
        result = []
        data = []
        # connect database sky007_test
        db = pymysql.connect(host='61.100.180.32', port=3306, user='root', passwd="dorcmdnjs123#AB#", database='sky007v2')
        cur = db.cursor(pymysql.cursors.DictCursor)


        cur.execute(query, (databody['startDate'], databody['endDate']))

        # map variable cur save data to database
        for row in cur:
            data.append(row)

        cur.close()
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

        return Response({
            'status': 'ok',
            'message': 'Sync data to google sheets successfully.',
            # 'data': result
        })

# Create your views here.
@api_view(['POST'])
def sync_report_data_to_googlesheet(request):
    if request.method == 'POST':
        databody = json.loads(request.body)
        CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

        query = "SELECT p.id, n.date_time AS create_time,\
                n.ord_category,\
                MAX( CASE WHEN p_m.meta_key = '_billing_phone' AND p.ID = p_m.post_id THEN p_m.meta_value END ) AS `phone_number`,\
                MAX( CASE WHEN p_m.meta_key = '_shipping_first_name' AND p.ID = p_m.post_id THEN p_m.meta_value END ) AS `name`,\
                MAX( CASE WHEN p_m.meta_key = '_order_total' AND p.ID = p_m.post_id THEN p_m.meta_value END ) AS `total_order`\
                FROM `aowp_posts` AS p\
                JOIN `aowp_postmeta` AS p_m ON p_m.post_id = p.id\
                JOIN `tb_ord_note` AS n ON p.id = n.order_id\
                JOIN `aowp_woocommerce_order_items` AS od_i ON od_i.order_id = p.id\
                JOIN `aowp_woocommerce_order_itemmeta` AS od_im ON od_im.order_item_id = od_i.order_item_id\
                WHERE p.post_status!='trash' AND  p.post_status != 'wc-cancelled' AND p.post_type='shop_order'\
                AND p.post_date BETWEEN %(startDate)s AND %(endDate)s\
                AND od_im.meta_key = '_product_id' AND od_i.order_item_type = 'line_item' AND od_im.meta_value IN %(productList)s\
                AND n.ord_category IN %(platform)s \
                GROUP BY p.id"
        
        db = pymysql.connect(host='61.100.180.32', port=3306, user='root', passwd="dorcmdnjs123#AB#", database='sky007v2')
        cur = db.cursor(pymysql.cursors.DictCursor)

        data = []
        result = []
        cur.execute(query, {
            'startDate': databody['startDate'], 'endDate': databody['endDate'],
            'productList': databody['productList'], 'platform': databody['platform']
        })

        # map variable cur save data to database
        for row in cur:
            data.append(row)

        cur.close()
        # clean data sent google sheets
        for row in data:
            arrTemp = []
            for obj in row:
                if obj == 'create_time':
                    arrTemp.append(row[obj].strftime("%m/%d/%Y %H:%M:%S"))
                elif obj == 'ord_category':
                    arrTemp.append(get_name_platform(row[obj]))
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

        return Response({
            'status': 'ok',
            'message': 'Sync data to google sheets successfully.',
            # 'data': result
        })

def get_name_platform(id):
    match id:
        case "0":
            return "Website"
        case "46":
            return "Website"
        case "48":
            return "Website"
        case "10":
            return "Shopee"
        case "20":
            return "Lazada"
        case "36":
            return "Tiki"
        case "58":
            return "TikTok"
        case _:
            print("The language doesn't matter, what matters is solving problems.")

# Create your views here.
@api_view(['GET'])
def get_list_post(request):
    if request.method == 'GET':
        brand = request.query_params.get("brand", None)

        db = pymysql.connect(host='61.100.180.32', port=3306, user='root', passwd="dorcmdnjs123#AB#", database='sky007v2')
        cur = db.cursor(pymysql.cursors.DictCursor)

        if(brand and brand != 'null'):
            if(brand == "BA"):
                condition = "AND ( sku LIKE '" + brand + "%' OR  sku LIKE 'B" + brand + "%')"
            else:
                condition = "AND sku LIKE '" + brand + "%'"

        query = "SELECT product_id,product_name,sku FROM `tb_stock_divide`\
        WHERE type_combo=0 AND  sku NOT LIKE '%gif%' AND sku NOT LIKE '%gf%' AND  sku  LIKE '%-R'"

        if(brand and brand != 'null'):
            cur.execute(query + condition)
        else:
            cur.execute(query)
       
        data = []
        for row in cur:
            data.append(row)

        cur.close()


        return Response({
            'status': 'ok',
            'data': data,
        })