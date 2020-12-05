import numpy as np
import pandas as pd

# Chuyển đổi giá về dạng số và cột


def convertPrice(prices):
    priceTypes = ['priceConcurrent', 'priceUnder500', 'price500-800', 'price800-1', 'price1-3',
                  'price3-5', 'price5-7', 'price7-10', 'price10-20', 'price20-30', 'priceOver30']
    default = np.zeros(shape=(len(prices), len(priceTypes)))
    numberOfPrices = pd.DataFrame(default, columns=priceTypes)

    for price in range(len(prices)):
        prices[price] = int(prices[price])
        if(prices[price] == 0):
            numberOfPrices.iloc[price][priceTypes[0]] = 1
        if(0 < prices[price] <= 500000000):
            numberOfPrices.iloc[price][priceTypes[1]] = 1
        if(500000000 < prices[price] <= 800000000):
            numberOfPrices.iloc[price][priceTypes[2]] = 1
        if(800000000 < prices[price] <= 1000000000):
            numberOfPrices.iloc[price][priceTypes[3]] = 1
        if(1000000000 < prices[price] <= 3000000000):
            numberOfPrices.iloc[price][priceTypes[4]] = 1
        if(3000000000 < prices[price] <= 5000000000):
            numberOfPrices.iloc[price][priceTypes[5]] = 1
        if(5000000000 < prices[price] <= 7000000000):
            numberOfPrices.iloc[price][priceTypes[6]] = 1
        if(7000000000 < prices[price] <= 10000000000):
            numberOfPrices.iloc[price][priceTypes[7]] = 1
        if(10000000000 < prices[price] <= 20000000000):
            numberOfPrices.iloc[price][priceTypes[8]] = 1
        if(20000000000 < prices[price] <= 30000000000):
            numberOfPrices.iloc[price][priceTypes[9]] = 1
        if(prices[price] > 30000000000):
            numberOfPrices.iloc[price][priceTypes[10]] = 1
    return numberOfPrices

# END - Chuyển đổi giá về dạng số và cột

# Chuyển đổi diện tích về dạng số và cột


def convertArea(areas):
    areaTypes = ['areaUndefine', 'areaUnder30', 'area30-50', 'area50-70', 'area70-100',
                 'area100-150', 'area150-200', 'area200-300', 'area300-500', 'area500-1000', 'areaOver1000']
    default = np.zeros(shape=(len(areas), len(areaTypes)))
    numberOfAreas = pd.DataFrame(default, columns=areaTypes)

    for area in range(len(areas)):
        areas[area] = float(areas[area])
        if(areas[area] == 0):
            numberOfAreas.iloc[area][areaTypes[0]] = 1
        if(0 < areas[area] <= 30):
            numberOfAreas.iloc[area][areaTypes[1]] = 1
        if(30 < areas[area] <= 50):
            numberOfAreas.iloc[area][areaTypes[2]] = 1
        if(50 < areas[area] <= 70):
            numberOfAreas.iloc[area][areaTypes[3]] = 1
        if(70 < areas[area] <= 100):
            numberOfAreas.iloc[area][areaTypes[4]] = 1
        if(100 < areas[area] <= 150):
            numberOfAreas.iloc[area][areaTypes[5]] = 1
        if(150 < areas[area] <= 200):
            numberOfAreas.iloc[area][areaTypes[6]] = 1
        if(200 < areas[area] <= 300):
            numberOfAreas.iloc[area][areaTypes[7]] = 1
        if(300 < areas[area] <= 500):
            numberOfAreas.iloc[area][areaTypes[8]] = 1
        if(500 < areas[area] <= 1000):
            numberOfAreas.iloc[area][areaTypes[9]] = 1
        if(areas[area] > 100):
            numberOfAreas.iloc[area][areaTypes[10]] = 1
    return numberOfAreas

# END - Chuyển đổi diện tích về dạng số và cột

# Chuyển đổi phòng ngủ về dạng số và cột


def convertBedrooms(bedrooms):
    bedroomTypes = ['bedroomUndefine', 'bedroom1', 'bedroom2', 'bedroom3', 'bedroom4',
                    'bedroom5', 'bedroom6', 'bedroom7', 'bedroom8', 'bedroom9', 'bedroomOver9']
    default = np.zeros(shape=(len(bedrooms), len(bedroomTypes)))
    numberOfBedrooms = pd.DataFrame(default, columns=bedroomTypes)

    for bedroom in range(len(bedrooms)):
        bedrooms[bedroom] = int(bedrooms[bedroom])
        if(bedrooms[bedroom] == 0):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[0]] = 1
        if(bedrooms[bedroom] == 1):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[1]] = 1
        if(bedrooms[bedroom] == 2):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[2]] = 1
        if(bedrooms[bedroom] == 3):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[3]] = 1
        if(bedrooms[bedroom] == 4):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[4]] = 1
        if(bedrooms[bedroom] == 5):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[5]] = 1
        if(bedrooms[bedroom] == 6):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[6]] = 1
        if(bedrooms[bedroom] == 7):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[7]] = 1
        if(bedrooms[bedroom] == 8):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[8]] = 1
        if(bedrooms[bedroom] == 9):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[9]] = 1
        if(bedrooms[bedroom] > 9):
            numberOfBedrooms.iloc[bedroom][bedroomTypes[10]] = 1
    return numberOfBedrooms

# END - Chuyển đổi phòng ngủ về dạng số và cột

# Chuyển đổi tầng về dạng số và cột


def convertFloors(floors):
    floorTypes = ['floorUndefine', 'floor1', 'floor2', 'floor3', 'floor4',
                  'floor5', 'floor6', 'floor7', 'floor8', 'floor9', 'floorOver9']
    default = np.zeros(shape=(len(floors), len(floorTypes)))
    numberOfFloors = pd.DataFrame(default, columns=floorTypes)

    for floor in range(len(floors)):
        floors[floor] = int(floors[floor])
        if(floors[floor] == 0):
            numberOfFloors.iloc[floor][floorTypes[0]] = 1
        if(floors[floor] == 1):
            numberOfFloors.iloc[floor][floorTypes[1]] = 1
        if(floors[floor] == 2):
            numberOfFloors.iloc[floor][floorTypes[2]] = 1
        if(floors[floor] == 3):
            numberOfFloors.iloc[floor][floorTypes[3]] = 1
        if(floors[floor] == 4):
            numberOfFloors.iloc[floor][floorTypes[4]] = 1
        if(floors[floor] == 5):
            numberOfFloors.iloc[floor][floorTypes[5]] = 1
        if(floors[floor] == 6):
            numberOfFloors.iloc[floor][floorTypes[6]] = 1
        if(floors[floor] == 7):
            numberOfFloors.iloc[floor][floorTypes[7]] = 1
        if(floors[floor] == 8):
            numberOfFloors.iloc[floor][floorTypes[8]] = 1
        if(floors[floor] == 9):
            numberOfFloors.iloc[floor][floorTypes[9]] = 1
        if(floors[floor] > 9):
            numberOfFloors.iloc[floor][floorTypes[10]] = 1
    return numberOfFloors

# END - Chuyển đổi tầng về dạng số và cột

# Chuyển đổi tầng về dạng số và cột


def convertDirections(directions):
    directionTypes = ['directionUndefine', 'east', 'west', 'south', 'north',
                      'east-north', 'west-north', 'east-south', 'west-south']
    default = np.zeros(shape=(len(directions), len(directionTypes)))
    numberOfDirections = pd.DataFrame(default, columns=directionTypes)

    for direction in range(len(directions)):
        directions[direction] = int(directions[direction])
        if(directions[direction] == 0):
            numberOfDirections.iloc[direction][directionTypes[0]] = 1
        if(directions[direction] == 1):
            numberOfDirections.iloc[direction][directionTypes[1]] = 1
        if(directions[direction] == 2):
            numberOfDirections.iloc[direction][directionTypes[2]] = 1
        if(directions[direction] == 3):
            numberOfDirections.iloc[direction][directionTypes[3]] = 1
        if(directions[direction] == 4):
            numberOfDirections.iloc[direction][directionTypes[4]] = 1
        if(directions[direction] == 5):
            numberOfDirections.iloc[direction][directionTypes[5]] = 1
        if(directions[direction] == 6):
            numberOfDirections.iloc[direction][directionTypes[6]] = 1
        if(directions[direction] == 7):
            numberOfDirections.iloc[direction][directionTypes[7]] = 1
        if(directions[direction] == 8):
            numberOfDirections.iloc[direction][directionTypes[8]] = 1
    return numberOfDirections

# END - Chuyển đổi tầng về dạng số và cột

# Xử lý các thuộc tính


def changeProperties(data):
    # Xử lý các chữ và NaN và chuẩn hóa
    data['Price'] = data['Price'].fillna(0)
    data['Area'] = data['Area'].str.replace('m²', '').fillna(0)
    try:
        data['Bedrooms'] = data['Bedrooms'].str.replace(
            '\(phòng\)', '').fillna(0)
    except:
        data['Bedrooms'] = data['Bedrooms'].fillna(0)
    try:
        data['Floors'] = data['Floors'].str.replace('\(tầng\)', '').fillna(0)
    except:
        data['Floors'] = data['Floors'].fillna(0)
    data['Direction'] = data['Direction'].str.replace('Đông-Bắc', '5').str.replace('Tây-Bắc', '6').str.replace('Đông-Nam', '7').str.replace(
        'Tây-Nam', '8').str.replace('Đông', '1').str.replace('Tây', '2').str.replace('Nam', '3').str.replace('Bắc', '4').fillna(0)

    # Ép kiểu cho các thuộc tính
    for i in range(len(data.index)):
        data['Price'].values[i] = str(data['Price'].values[i])
        data['Area'].values[i] = float(data['Area'].values[i])
        data['Bedrooms'].values[i] = int(data['Bedrooms'].values[i])
        data['Floors'].values[i] = int(data['Floors'].values[i])
        data['Direction'].values[i] = int(data['Direction'].values[i])
        data['District'].values[i] = int(data['District'].values[i])

    return data
# END - Xử lý các thuộc tính

# Xử lý giá về dạng đầy đủ


def changePrice(array):
    arrayTemp = []
    for price in array:
        if("Thỏa thuận" in price):
            price = price.replace("Thỏa thuận", "0").strip()
            arrayTemp.append(price)
        if ("tỷ" in price):
            price = price.replace("tỷ", "").strip()
            if("." in price):
                if(len(price.split('.')[1]) == 1):
                    arrayTemp.append(price.replace(".", "")+"00000000")
                if(len(price.split('.')[1]) == 2):
                    arrayTemp.append(price.replace(".", "")+"0000000")
                if(len(price.split('.')[1]) == 3):
                    arrayTemp.append(price.replace(".", "")+"000000")
            if("." not in price):
                arrayTemp.append(price+"000000000")
        if("triệu/m²" in price):
            arrayTemp.append("0")
        else:
            if("triệu" in price):
                price = price.replace("triệu", "").strip()
                if("." in price):
                    if(len(price.split('.')[1]) == 1):
                        arrayTemp.append(price.replace(".", "")+"00000")
                    if(len(price.split('.')[1]) == 2):
                        arrayTemp.append(price.replace(".", "")+"0000")
                    if(len(price.split('.')[1]) == 3):
                        arrayTemp.append(price.replace(".", "")+"000")
                if("." not in price):
                    arrayTemp.append(price+"000000")
    return arrayTemp
# END - Xử lý giá về dạng đầy đủ

# Ưu tiên cho thuộc tính


def priority(value, type, rating, data):
    priceTypes = ['priceConcurrent', 'priceUnder500', 'price500-800', 'price800-1', 'price1-3',
                  'price3-5', 'price5-7', 'price7-10', 'price10-20', 'price20-30', 'priceOver30']
    areaTypes = ['areaUndefine', 'areaUnder30', 'area30-50', 'area50-70', 'area70-100',
                 'area100-150', 'area150-200', 'area200-300', 'area300-500', 'area500-1000', 'areaOver1000']
    bedroomTypes = ['bedroomUndefine', 'bedroom1', 'bedroom2', 'bedroom3', 'bedroom4',
                    'bedroom5', 'bedroom6', 'bedroom7', 'bedroom8', 'bedroom9', 'bedroomOver9']
    floorTypes = ['floorUndefine', 'floor1', 'floor2', 'floor3', 'floor4',
                  'floor5', 'floor6', 'floor7', 'floor8', 'floor9', 'floorOver9']
    directionTypes = ['directionUndefine', 'east', 'west', 'south', 'north',
                      'east-north', 'west-north', 'east-south', 'west-south']

    if(type == "price"):
        if(value == 0):
            data[priceTypes[0]] = data[priceTypes[0]] * rating
        if(0 < value <= 500000000):
            data[priceTypes[1]] = data[priceTypes[1]] * rating
        if(500000000 < value <= 800000000):
            data[priceTypes[2]] = data[priceTypes[2]] * rating
        if(800000000 < value <= 1000000000):
            data[priceTypes[3]] = data[priceTypes[3]] * rating
        if(1000000000 < value <= 3000000000):
            data[priceTypes[4]] = data[priceTypes[4]] * rating
        if(3000000000 < value <= 5000000000):
            data[priceTypes[5]] = data[priceTypes[5]] * rating
        if(5000000000 < value <= 7000000000):
            data[priceTypes[6]] = data[priceTypes[6]] * rating
        if(7000000000 < value <= 10000000000):
            data[priceTypes[7]] = data[priceTypes[7]] * rating
        if(10000000000 < value <= 20000000000):
            data[priceTypes[8]] = data[priceTypes[8]] * rating
        if(20000000000 < value <= 30000000000):
            data[priceTypes[9]] = data[priceTypes[9]] * rating
        if(20000000000 < value <= 30000000000):
            data[priceTypes[10]] = data[priceTypes[10]] * rating
    if(type == "area"):
        if(value == 0):
            data[areaTypes[0]] = data[areaTypes[0]] * rating
        if(0 < value <= 30):
            data[areaTypes[1]] = data[areaTypes[1]] * rating
        if(30 < value <= 50):
            data[areaTypes[2]] = data[areaTypes[2]] * rating
        if(50 < value <= 70):
            data[areaTypes[3]] = data[areaTypes[3]] * rating
        if(70 < value <= 100):
            data[areaTypes[4]] = data[areaTypes[4]] * rating
        if(100 < value <= 150):
            data[areaTypes[5]] = data[areaTypes[5]] * rating
        if(150 < value <= 200):
            data[areaTypes[6]] = data[areaTypes[6]] * rating
        if(200 < value <= 300):
            data[areaTypes[7]] = data[areaTypes[7]] * rating
        if(300 < value <= 500):
            data[areaTypes[8]] = data[areaTypes[8]] * rating
        if(500 < value <= 1000):
            data[areaTypes[9]] = data[areaTypes[9]] * rating
        if(value > 100):
            data[areaTypes[10]] = data[areaTypes[10]] * rating
    if(type == "bedrooms"):
        if(value == 0):
            data[bedroomTypes[0]] = data[bedroomTypes[0]] * rating
        if(value == 1):
            data[bedroomTypes[1]] = data[bedroomTypes[1]] * rating
        if(value == 2):
            data[bedroomTypes[2]] = data[bedroomTypes[2]] * rating
        if(value == 3):
            data[bedroomTypes[3]] = data[bedroomTypes[3]] * rating
        if(value == 4):
            data[bedroomTypes[4]] = data[bedroomTypes[4]] * rating
        if(value == 5):
            data[bedroomTypes[5]] = data[bedroomTypes[5]] * rating
        if(value == 6):
            data[bedroomTypes[6]] = data[bedroomTypes[6]] * rating
        if(value == 7):
            data[bedroomTypes[7]] = data[bedroomTypes[7]] * rating
        if(value == 8):
            data[bedroomTypes[8]] = data[bedroomTypes[8]] * rating
        if(value == 9):
            data[bedroomTypes[9]] = data[bedroomTypes[9]] * rating
        if(value > 9):
            data[bedroomTypes[10]] = data[bedroomTypes[10]] * rating
    if(type == "floors"):
        if(value == 0):
            data[floorTypes[0]] = data[floorTypes[0]] * rating
        if(value == 1):
            data[floorTypes[1]] = data[floorTypes[1]] * rating
        if(value == 2):
            data[floorTypes[2]] = data[floorTypes[2]] * rating
        if(value == 3):
            data[floorTypes[3]] = data[floorTypes[3]] * rating
        if(value == 4):
            data[floorTypes[4]] = data[floorTypes[4]] * rating
        if(value == 5):
            data[floorTypes[5]] = data[floorTypes[5]] * rating
        if(value == 6):
            data[floorTypes[6]] = data[floorTypes[6]] * rating
        if(value == 7):
            data[floorTypes[7]] = data[floorTypes[7]] * rating
        if(value == 8):
            data[floorTypes[8]] = data[floorTypes[8]] * rating
        if(value == 9):
            data[floorTypes[9]] = data[floorTypes[9]] * rating
        if(value > 9):
            data[floorTypes[10]] = data[floorTypes[10]] * rating
    if(type == "directions"):
        if(value == 0):
            data[directionTypes[0]] = data[directionTypes[0]] * rating
        if(value == 1):
            data[directionTypes[1]] = data[directionTypes[1]] * rating
        if(value == 2):
            data[directionTypes[2]] = data[directionTypes[2]] * rating
        if(value == 3):
            data[directionTypes[3]] = data[directionTypes[3]] * rating
        if(value == 4):
            data[directionTypes[4]] = data[directionTypes[4]] * rating
        if(value == 5):
            data[directionTypes[5]] = data[directionTypes[5]] * rating
        if(value == 6):
            data[directionTypes[6]] = data[directionTypes[6]] * rating
        if(value == 7):
            data[directionTypes[7]] = data[directionTypes[7]] * rating
        if(value == 8):
            data[directionTypes[8]] = data[directionTypes[8]] * rating
    return data
# END - Ưu tiên cho thuộc tính
