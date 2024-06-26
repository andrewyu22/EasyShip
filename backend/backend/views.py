from django.http import JsonResponse
from rest_framework.decorators import api_view
from .azure import analyze_document
from django.core.files.storage import FileSystemStorage
import traceback
import requests
import re
import json
import logging

# Ensure you import the necessary functions:
# from your_module import analyze_document, getToken

logger = logging.getLogger(__name__)

@api_view(['POST'])
def analyze_document_view(request):
    if request.method == 'POST' and request.FILES.get('document'):
        document = request.FILES['document']
        fs = FileSystemStorage()
        filename = fs.save(document.name, document)
        file_path = fs.path(filename)
        extracted_data = {}
        try:
            logger.debug(f"Analyzing document: {file_path}")
            result = analyze_document(file_path)
            for doc in result.documents: 
                for field_name, field_value in doc.fields.items():
                    extracted_data[field_name] = field_value.value
            token = getToken()
<<<<<<< HEAD
            logger.debug(f"Extracted data: {extracted_data}")
            return JsonResponse(extracted_data)
=======
            print(extracted_data)

>>>>>>> c89fc6495214362fcebe2d948531bc6dae5ce249
        except Exception as e:
            logger.error(f"Error analyzing document: {traceback.format_exc()}")
            return JsonResponse({'error': str(e)}, status=500)

    logger.warning("Invalid request: Missing document or wrong method.")
    return JsonResponse({'error': 'Invalid request'}, status=400)

def getToken():
    url = "https://api-sandbox.sendpro360.pitneybowes.com/auth/api/v1/token"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, auth=('0oa23mqvko29TZGcx0h8','ngVxjPIkGlcJP7Dpgs_coOiRohTh_MDxF4oba3pkz4tz1HkQ1GuW2UsFY7cU_Iur'))
    data = response.json()
    return data


def parse_item_dimension(item_dimension):
    # Match patterns like '10 IN x 8 IN x 4 IN'
    pattern_in = re.compile(r'(\d+)\s*IN\s*x\s*(\d+)\s*IN\s*x\s*(\d+)\s*IN')
    # Match patterns like '24"*24"*48"' or '18"*6"*2"'
    pattern_quote = re.compile(r'(\d+)"\s*x\s*(\d+)"\s*x\s*(\d+)"')
    
    if pattern_in.match(item_dimension):
        match = pattern_in.match(item_dimension)
        length = int(match.group(1))
        width = int(match.group(2))
        height = int(match.group(3))
        unit = 'IN'
    elif pattern_quote.match(item_dimension):
        match = pattern_quote.match(item_dimension)
        length = int(match.group(1))
        width = int(match.group(2))
        height = int(match.group(3))
        unit = 'IN'
    else:
        raise ValueError(f"Invalid item dimension format: {item_dimension}")
    
    return {
        'length': length,
        'width': width,
        'height': height,
        'dimUnit': unit
    }


def getSingleRate(token, shippingData):
    url = "https://api-sandbox.sendpro360.pitneybowes.com/shipping/api/v1/rates"
    parse_dim = parse_item_dimension(shippingData['ItemDimension'])
    payload = {
        "dateOfShipment": shippingData['OrderDate'],
        "fromAddress": {
            "addressLine1": shippingData['ShipFromAddress'],
            "cityTown": shippingData['ShipFromCity'],
            "company": shippingData['ShipFromName'],
            "countryCode": "US",
            "email": "sender@email.com",
            "name": "John Doe",
            "phone": shippingData['ShipFromPhone'],
            "postalCode": shippingData['ShipFromZip'],
            "stateProvince": shippingData['ShipFromState'],
            "residential": False
        },
        "parcel": {
            "height": parse_dim['height'],
            "length": parse_dim['length'],
            "width": parse_dim['width'],
            "dimUnit": parse_dim['dimUnit'],
            "weightUnit": "OZ",
            "weight": 1
        },
        "carrierAccounts": [
            "12prrs1"
        ],
        "parcelType": "FRE",
        "parcelId": "FRE",
        "serviceId": "PM",
        "specialServices": [
            {
            "inputParameters": [
                {
                "name": "INPUT_VALUE",
                "value": "100"
                }
            ],
            "specialserviceId": "Ins"
            }
        ],
        "toAddress": {
            "addressLine1": shippingData['ShipToAddress'],
            "cityTown": shippingData['ShipToCity'],
            "company": "Pitney Bowes Inc.",
            "countryCode": "US",
            "email": "receiver@email.com",
            "name": shippingData['ShipToName'],
            "phone": "2032032033",
            "postalCode": shippingData['ShipToZip'],
            "residential": True,
            "stateProvince": shippingData['ShipToState']
        }
    }

    print(json.dumps(payload))
    headers = {
        "Content-Type": "application/json",
        "X-PB-Developer-Partner-ID": "string",
        "compactResponse": "true",
        "Authorization": f"Bearer {token['access_token']}"
    }
    # response = requests.post(url, json=payload, headers=headers)
    # data = response.json()
    return 'data'


def getCarrier(token, carrierName):
    url = "https://api-sandbox.sendpro360.pitneybowes.com/shipping/api/v1/services"
    query = {
        "carrier": carrierName,
        "originCountryCode": "US",
        "destinationCountryCode": "US"
    }

    headers = {
        "X-PB-Developer-Partner-ID": "string",
        "Authorization": f"Bearer {token['access_token']}"
    }
    response = requests.get(url, headers=headers, params=query)
    data = response.json()
    return data