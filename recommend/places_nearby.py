import pandas as pd
import numpy as np
import pprint
import urllib.request
import json
from slugify import slugify, Slugify, UniqueSlugify

# Lấy vĩ độ kinh độ từ địa chỉ


def locationFromAddress(address):
    try:
        add = slugify(address, to_lower=True)  # 'any-text'
        with urllib.request.urlopen("https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey=2EqdUFT8C-onbX-jDWsv5vcl_Y-iy8aISIe3LxiU5Uk&searchtext="+add) as url:
            data = json.loads(url.read().decode())
            # pprint.pprint(data)
            # pprint.pprint(data['Response']['View'][0]['Result']
            #               [0]['Location']['DisplayPosition'])
            latitude = data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude']
            longitude = data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude']

    except:
        addTemp = address.split(',')
        addTemp.pop(0)
        addOke = ",".join(addTemp).strip()

        return locationFromAddress(addOke)

    return latitude, longitude

# print(locationFromAddress("Phường Phước Thới, Ô Môn, Cần Thơ"))
# END - Lấy vĩ độ kinh độ từ địa chỉ

# Lấy địa điểm lân cận băng vĩ độ kinh độ


def getPlacesNearby(latitude, longitude, radius):
    app_id = "DemoAppId01082013GAL"
    app_code = "AJKnXv84fjrb0KIHawS0Tg"
    places = []  # Mảng lưu các địa điểm lân cận
    with urllib.request.urlopen("https://places.demo.api.here.com/places/v1/discover/around?app_id=" + app_id + "&app_code=" + app_code + "&at=" + str(latitude) + "," + str(longitude) + "%3Br%3Dr" + str(radius) + "&size=2147483647") as url:
        data = json.loads(url.read().decode())
        # pprint.pprint(data['results']['items'][0]['category']['id'])
        for i in range(0, len(data['results']['items'])):
            place = data['results']['items'][i]['category']['id']
            places.append(place)
        # df = pd.json_normalize(data['results']['items'])
        # print(df)
    return list(set(places))

# END - Lấy địa điểm lân cận băng vĩ độ kinh độ

# Lấy các địa điểm lân cận


def donePlaces(address):
    radius = 2000
    latitude, longitude = locationFromAddress(address)
    return getPlacesNearby(latitude, longitude, radius)


# places = donePlaces("Đường Nguyễn Văn Cừ, Phường An Khánh, Ninh Kiều, Cần Thơ")
# print(places)
# END - Lấy các địa điểm lân cận


# Chuyển các địa điểm lân cận về dạng số 1/0 (có hoặc không)
categories = ['eat-drink', 'restaurant', 'snacks-fast-food', 'bar-pub', 'coffee-tea', 'coffee', 'tea', 'going-out', 'dance-night-club', 'cinema', 'theatre-music-culture', 'casino', 'sights-museums', 'landmark-attraction', 'museum',
              'transport', 'airport', 'railway-station', 'public-transport', 'ferry-terminal', 'taxi-stand', 'accommodation', 'hotel', 'motel', 'hostel', 'camping', 'shopping', 'kiosk-convenience-store', 'wine-and-liquor', 'mall', 'department-store', 'food-drink', 'bookshop', 'pharmacy', 'electronics-shop', 'hardware-house-garden-shop', 'clothing-accessories-shop', 'sport-outdoor-shop', 'shop', 'business-services', 'atm-bank-exchange', 'police-emergency', 'ambulance-services', 'fire-department', 'police-station', 'post-office', 'tourist-information', 'petrol-station', 'ev-charging-station', 'car-rental', 'car-dealer-repair', 'travel-agency', 'communication-media', 'business-industry', 'service', 'facilities', 'hospital-health-care-facility', 'hospital', 'government-community-facility', 'education-facility', 'library', 'fair-convention-facility', 'parking-facility', 'toilet-rest-area', 'sports-facility-venue', 'facility', 'religious-place', 'leisure-outdoor', 'recreation', 'amusement-holiday-park', 'zoo', 'administrative-areas-buildings', 'administrative-region', 'city-town-village', 'outdoor-area-complex', 'building', 'street-square', 'intersection', 'postal-area', 'natural-geographical', 'body-of-water', 'mountain-hill', 'undersea-feature', 'forest-heath-vegetation']


def convertNumber(placesNearbys):
    default = np.zeros(shape=(len(placesNearbys), len(categories)))
    # print(array)
    numberOfPN = pd.DataFrame(default, columns=categories)
    # print(numberOfPN)
    # print(numberOfPN.iloc[0, 1])
    count = 0
    for placesNearby in placesNearbys:
        for places in placesNearby:
            for categorie in categories:
                if(places == categorie):
                    # print(count)
                    numberOfPN.loc[count][categorie] = 1
        count += 1
    return numberOfPN


# print(convertNumber(places))
# END - Chuyển các địa điểm lân cận về dạng số 1/0 (có hoặc không)
