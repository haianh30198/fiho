import pandas as pd
import numpy as np
from slugify import slugify, Slugify, UniqueSlugify
from recommend.convert_5_properties import *
from recommend.places_nearby import convertNumber

categories = ['eat-drink', 'restaurant', 'snacks-fast-food', 'bar-pub', 'coffee-tea', 'coffee', 'tea',
              'going-out', 'dance-night-club', 'cinema', 'theatre-music-culture', 'casino',
              'sights-museums', 'landmark-attraction', 'museum',
              'transport', 'airport', 'railway-station', 'public-transport', 'ferry-terminal', 'taxi-stand',
              'accommodation', 'hotel', 'motel', 'hostel', 'camping',
              'shopping', 'kiosk-convenience-store', 'wine-and-liquor', 'mall',
              'department-store', 'food-drink', 'bookshop', 'pharmacy', 'electronics-shop', 'hardware-house-garden-shop', 'clothing-accessories-shop', 'sport-outdoor-shop', 'shop',
              'business-services', 'atm-bank-exchange', 'police-emergency', 'ambulance-services', 'fire-department', 'police-station', 'post-office', 'tourist-information', 'petrol-station', 'ev-charging-station',
              'car-rental', 'car-dealer-repair', 'travel-agency', 'communication-media', 'business-industry', 'service',
              'facilities', 'hospital-health-care-facility', 'hospital', 'government-community-facility', 'education-facility', 'library', 'fair-convention-facility', 'parking-facility', 'toilet-rest-area', 'sports-facility-venue', 'facility',
              'religious-place', 'leisure-outdoor', 'recreation', 'amusement-holiday-park', 'zoo',
              'administrative-areas-buildings', 'administrative-region', 'city-town-village', 'outdoor-area-complex', 'building', 'street-square', 'intersection', 'postal-area',
              'natural-geographical', 'body-of-water', 'mountain-hill', 'undersea-feature', 'forest-heath-vegetation']

dictPlaces = {
    'eat-drink': ['eat-drink', 'an-uong'],
    'restaurant': ['restaurant', 'nha-hang', 'quan-an', 'quan-hu-hieu', 'tiem-an', 'tiem-hu-tieu'],
    'snacks-fast-food': ['snacks-fast-food', 'kfc', 'lotteria', 'tiem-an-nhanh', 'quan-an-nhanh', 'le-trang', 'xe-banh-mi', 'xe-banh-my', 'tiem-banh-mi', 'tiem-banh-my'],
    'bar-pub': ['bar', 'pub', 'bar-pub'],
    'coffee-tea': ['coffee-tea'],
    'coffee': ['coffee', 'tiem-ca-phe', 'quan-ca-phe', 'tiem-cafe', 'quan-cafe', 'tiem-coffee', 'quan-coffee', 'ca-phe'],
    'tea': ['tea', 'tiem-tra', 'quan-tra', 'tra-sua', 'quan-tra-sua', 'tiem-tra-sua'],
    'going-out': ['going-out'],
    'dance-night-club': ['dance-night-club', 'bar', 'pub', 'bar-pub', 'karaoke', 'quan-karaoke', 'tiem-karaoke', 'cau-lac-bo-guitar', 'nhay-dam', 'quan-bia', 'tiem-bia', 'cau-lac-bo-nhay-mua', 'zumba', 'cau-lac-bo-zumba', 'quan-ruou', 'tiem-ruou'],
    'cinema': ['cinema', 'rap-xem-phim', 'rap-phim', 'rap-chieu-bong'],
    'theatre-music-culture': ['theatre-music-culture', 'nha-hat', 'san-khau', 'nha-van-hoa', 'bieu-dien-nghe-thuat'],
    'casino': ['casino', 'song-bac', 'song-bai', 'casino'],
    'sights-museums': ['sights-museums'],
    'landmark-attraction': ['landmark-attraction', 'ben-ninh-kieu', 'khu-du-lich', 'cho-noi', 'chua', 'trien-lam', 'khu-di-tich-lich-su', 'khu-di-tich', 'nha-may-bia'],
    'museum': ['museum', 'vien-bao-tang', 'bao-tang-nghe-thuat', 'bao-tang-tre-em', 'bao-tang-khoa-hoc', 'bao-tang'],
    'transport': ['transport', 'ben-xe'],
    'airport': ['airport', 'san-bay', 'san-bay-can-tho', 'san-bay-tan-son-nhat', 'san-bay-the-thao-cong-cong', 'san-bay-the-thao', 'tram-san-bay'],
    'railway-station': ['railway-station', 'duong-sat', 'ga-tau-xe-lua', 'ga-tau'],
    'public-transport': ['public-transport', 'ben-xe', 'tram-xe-buyt', 'tram-xe-lua', 'tau-dien-ngam', 'tram-dung-xe-buyt', 'ben-pha', 'pha', 'pha-duong-sat', 'taxi', 'loi-ra-duong-cao-toc', 'nha-thu-phi', 'tram-thu-phi', 'bot', 'duong-xe-dien-tren-khong', 'bai-xe-dap'],
    'ferry-terminal': ['ferry-terminal'],
    'taxi-stand': ['taxi-stand', 'taxi', 'tram-taxi', 'ben-taxi'],
    'accommodation': ['accommodation'],
    'hotel': ['khach-san', 'hotel', 'nha-khach'],
    'motel': ['nha-nghi', 'motel', 'nha-khach'],
    'hostel': ['nha-tro', 'hostel'],
    'camping': ['camping', 'khu-cam-trai', 'bai-cam-trai'],
    'shopping': ['shopping'],
    'kiosk-convenience-store': ['kiosk-convenience-store', 'cua-hang-tien-loi', 'cua-hang-bach-hoa', 'bach-hoa', 'cua-hang-bach-hoa'],
    'wine-and-liquor': ['wine-and-liquor', 'cua-hang-ruou'],
    'mall': ['mall', 'trung-tam-thuong-mai', 'trung-tam-mua-sam', 'sieu-thi'],
    'department-store': ['department-store', 'cua-hang-tap-hoa', 'tap-hoa', 'cua-hang-am-thuc', 'khu-am-thuc'],
    'food-drink': ['food-drink', 'cua-hang-banh-ngot', 'tiem-banh-ngot', 'tiem-ban-thit', 'cua-hang-thit', 'cua-hang-sua',  'cua-hang-thu-pham', 'cua-hang-trai-cay', 'cho', 'quan-nhau'],
    'bookshop': ['bookshop', 'cua-hang-sach', 'nha-sach', 'tiem-sach'],
    'pharmacy': ['pharmacy', 'nha-thuoc', 'tiem-thuoc', 'cua-hang-thuoc'],
    'electronics-shop': ['electronics-shop', 'tiem-dien', 'dien-nuoc', 'cua-hang-tien', 'ban-do-dien'],
    'hardware-house-garden-shop': ['hardware-house-garden-shop', 'cua-hang-ban-cay-canh', 'tiem-cay-canh', 'cay-canh'],
    'clothing-accessories-shop': ['clothing-accessories-shop', 'cua-hang-quan-ao', 'cua-hang-thoi-trang', 'quan-ao-nam', 'quan-ao-nu', 'shop-quan-ao', 'shop-thoi-trang'],
    'sport-outdoor-shop': ['sport-outdoor-shop', 'cua-hang-do-the-thao', 'thoi-trang-the-thao'],
    'shop': ['shop', 'do-an-cho-dong-vat', 'do-an-cho-cho', 'do-an-cho-cho-meo', 'cua-hang-do-choi'],
    'business-services': ['business-services'],
    'atm-bank-exchange': ['atm-bank-exchange', 'atm', 'ngan-hang', 'cay-atm'],
    'police-emergency': ['police-emergency', 'cong-an', 'canh-sat', 'don-canh-sat', 'don-cong-an'],
    'ambulance-services': ['ambulance-services', 'xe-cap-cuu', 'dich-vu-cap-cuu'],
    'fire-department': ['fire-department', 'cuu-hoa'],
    'police-station': ['police-station', 'cong-an-quan', 'cong-an-phuong', 'cong-an-thanh-pho'],
    'post-office': ['post-office', 'buu-dien'],
    'tourist-information': ['tourist-information', 'thuong-mai-du-lich', 'cong-ty-du-lich'],
    'petrol-station': ['petrol-station', 'cua-hang-xau-dau', 'xang', 'dau', 'xang-dau', 'cay-xang'],
    'ev-charging-station': ['ev-charging-station', 'tram-sac-dien', 'tru-sac-dien'],
    'car-rental': ['car-rental', 'cua-hang-thue-xe-o-to', 'thue-o-to', 'muon-o-to'],
    'car-dealer-repair': ['car-dealer-repair', 'sua-chua-xe-o-to', 'gara-sua-xe', 'gara-xe'],
    'travel-agency': ['travel-agency', 'tu-van-du-lich', 'du-lich'],
    'communication-media': ['communication-media', 'quang-cao', 'cong-ty-quang-cao-truyen-thong', 'truyen-thong'],
    'business-industry': ['business-industry', 'kinh-doanh'],
    'service': ['service', 'dich-vu'],
    'facilities': ['facilities'],
    'hospital-health-care-facility': ['hospital-health-care-facility', 'cham-soc-suc-khoe'],
    'hospital': ['hospital', 'tram-xa', 'benh-vien', 'tram-y-te'],
    'government-community-facility': ['government-community-facility', 'co-so-cong-dong-cua-chinh-phu'],
    'education-facility': ['education-facility', 'co-so-giao-duc', 'truong-tieu-hoc', 'truong-dai-hoc', 'truong-trung-hoc', 'giao-duc-thuong-xuyen', 'truong-hoc', 'tieu-hoc', 'trung-hoc'],
    'library': ['library', 'thu-vien'],
    'fair-convention-facility': ['fair-convention-facility', 'hoi-cho-co-so'],
    'parking-facility': ['parking-facility', 'bai-do-xe', 'bai-gui-xe'],
    'toilet-rest-area': ['toilet-rest-area', 'nha-ve-sinh-cong-cong', 'nha-ve-sinh-ngoai-troi'],
    'sports-facility-venue': ['sports-facility-venue', 'nha-thi-dau', 'nha-the-thao', 'san-van-dong', 'san-banh', 'san-bong', 'san-tenis', 'san-bong-ro', 'bida', 'golf'],
    'facility': ['facility', 'co-so'],
    'religious-place': ['religious-place', 'nha-tho', 'thanh-duong', 'chua', 'giao-duong', 'den', 'mieu', 'giao-hoi', 'an-vien', 'tu-vien', 'cong-dong-tu-vien', 'giao-duong-cua-hoi-giao', 'tho-cung'],
    'leisure-outdoor': ['leisure-outdoor', 'giai-tri-ngoai-troi', 'khu-vui-choi'],
    'recreation': ['recreation', 'giai-tri'],
    'amusement-holiday-park': ['amusement-holiday-park', 'cong-vien', 'cong-vien-giai-tri', 'cong-vien-ngoai-troi'],
    'zoo': ['zoo', 'so-thu', 'vuon-thu', 'bach-thu'],
    'administrative-areas-buildings': ['administrative-areas-buildings', 'khu-hanh-chinh'],
    'administrative-region': ['administrative-region', 'khu-vuc-hanh-chinh'],
    'city-town-village': ['city-town-village', 'thanh-pho', 'village', 'thon', 'xa'],
    'outdoor-area-complex': ['outdoor-area-complex', 'khu-phuc-hop'],
    'building': ['building', 'toa-nha', 'cao-oc'],
    'street-square': ['street-square', 'quang-truong'],
    'intersection': ['intersection', 'nga-tu'],
    'postal-area': ['postal-area', 'khu-vuc-buu-dien'],
    'natural-geographical': ['natural-geographical', 'dia-ly-tu-nhien', 'hang-dong'],
    'body-of-water': ['body-of-water', 'nuoc', 'song', 'suoi', 'ao', 'ho', 'thung-lung'],
    'mountain-hill': ['mountain-hill', 'doi', 'nui', 'doi-nui', 'nui-doi'],
    'undersea-feature': ['undersea-feature', 'tham-quan-duoi-bien'],
    'forest-heath-vegetation': ['forest-heath-vegetation', 'rung', 'khu-bao-ton-thien-nhien', 'khu-bao-ton']
}

array = ['cà phê', 'ăn uống', 'sông']  # Mảng địa điểm ngườu dùng nhập vào

# Địa điểm người dùng nhập quy đổi về danh mục


def userEnderPlacesNearby(array):
    placesNearby = []
    for place in array:
        place = slugify(place, to_lower=True)  # 'any-text'
        for key, value in dictPlaces.items():
            if(place in value):
                placesNearby.append(key)
    return list(set(placesNearby))

# print(userEnderPlacesNearby(array))
# END - Địa điểm người dùng nhập quy đổi về danh mục


def newData(price, area, bedrooms, floors, direction, placesNearby):
    # Chuẩn hóa giá
    priceDF = convertPrice([price])

    # Chuẩn hóa diện tích
    areaDF = convertArea([area])

    # Chuẩn hóa số phòng ngủ
    bedroomsDF = convertBedrooms([bedrooms])

    # Chuẩn hóa số tầng
    floorsDF = convertFloors([floors])

    # Chuẩn hóa hướng nhà
    directionsDF = convertDirections([direction])

    # Nối 5 thuộc tính lại
    propertiesDF = pd.concat(
        [priceDF, areaDF, bedroomsDF, floorsDF, directionsDF], axis=1)

    # Lấy địa điểm và chuẩn hóa về dạng số (placesNearby là 1 mảng các địa điểm lân cận)
    placesDF = convertNumber([userEnderPlacesNearby(placesNearby)])

    dataOfUser = pd.concat([propertiesDF, placesDF], axis=1)

    return dataOfUser
