from flask import Flask, request, jsonify
import sqlite3
import requests
import time
import os

app = Flask(__name__)


def init_db():

    db_path = os.path.abspath('places.db')
    
    conn = sqlite3.connect(db_path)
    # conn = sqlite3.connect('places.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            phone TEXT,
            website TEXT,
            rating REAL,
            types TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    return conn

def clear_db(conn):
    cur = conn.cursor()
    cur.execute('DELETE FROM places')
    conn.commit()

def insert_place(conn, place):
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO places (name, address, phone, website, rating, types, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        place['name'],
        place['address'],
        place['phone'],
        place['website'],
        place['rating'],
        ','.join(place['types']) if isinstance(place['types'], list) else '',
        place['status']
    ))
    conn.commit()

def get_place_details(api_key, place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'key': api_key,
        'place_id': place_id,
        'fields': 'website,formatted_phone_number'
    }

    response = requests.get(url, params=params, timeout=300)
    data = response.json()
    result = data.get('result', {})
    website = result.get('website')
    phone = result.get('formatted_phone_number')
    return website, phone

def get_places(api_key, location, radius, keyword='', type_='', has_website=False):

  
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'key': api_key,
        'location': location,
        'radius': radius,
    }
    if keyword:
        params['keyword'] = keyword
    if type_:
        params['type'] = type_
  
    results = []
    # conn = init_db()
    # clear_db(conn)

    while True:
        response = requests.get(url, params=params)
        data = response.json()
   

        for place in data.get('results', []):
            name = place.get('name')
            address = place.get('vicinity')
            place_id = place.get('place_id')
            rating = place.get('rating')
            types = place.get('types', [])
            business_status = place.get('business_status')
            website, phone = get_place_details(api_key, place_id)
           
           
            if has_website is False:
                if not website:  # only businesses with NO website
                    place_data = {
                        'name': name,
                        'address': address,
                        'phone': phone,
                        'website': website,
                        'rating': rating,
                        'types': types,
                        'status': business_status
                    }
                    results.append(place_data)
                    # insert_place(conn, place_data)
            elif has_website is True:
                if website:  # only businesses WITH a website
                    place_data = {
                        'name': name,
                        'address': address,
                        'phone': phone,
                        'website': website,
                        'rating': rating,
                        'types': types,
                        'status': business_status
                    }
                    results.append(place_data)
                    # insert_place(conn, place_data)
            else:
                # If has_website is None or any other value, include all
                    place_data = {
                        'name': name,
                        'address': address,
                        'phone': phone,
                        'website': website,
                        'rating': rating,
                        'types': types,
                        'status': business_status
                    }
                    results.append(place_data)
                    # insert_place(conn, place_data)

            



        # Paginate if there's more
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
        else:
            import time
            time.sleep(2)  # wait before using next_page_token
            params['pagetoken'] = next_page_token

    # conn.close()
    return results

# def get_place_details(api_key, place_id):
#     url = 'https://maps.googleapis.com/maps/api/place/details/json'
#     params = {
#         'key': api_key,
#         'place_id': place_id,
#         'fields': 'website,formatted_phone_number'
#     }

#     response = requests.get(url, params=params, timeout=300)
#     data = response.json()
#     result = data.get('result', {})
#     return result.get('website'), result.get('formatted_phone_number')


@app.route('/crawl', methods=['GET'])
def crawl_places():
    print(f"Received request: {request.args}")
    api_key = 'AIzaSyCAwaDlQXvVJ5H03aWHR8-WJ3zlvPPltws'
    location = request.args.get('location', '50.0405,-110.6766')
    radius = int(request.args.get('radius', 10000))
    keyword = request.args.get('keyword', '')

    has_website_param = request.args.get('has_website', 'both')

    has_website = None
    if has_website_param == 'yes':
        has_website = True
    elif has_website_param == 'no':
        has_website = False
    else:
        has_website = 'both'  # include all results regardless of website presence

    place_types_param = request.args.get('types', '')

    print(f"asdasdads {request}")
    if place_types_param:
            place_types = [p.strip() for p in place_types_param.split(',')]
    else:
        # fallback default types
        place_types = ['accounting', 'bakery', 'bank', 'bar']

    all_results = []
    for place_type in place_types:
        print(f"🔍 Searching for: {place_type}")
        results = get_places(api_key, location, radius, keyword, place_type, has_website=has_website)
        all_results.extend(results)

    return jsonify({
        "count": len(all_results),
        "results": all_results
    })


# --- Run the app ---
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5009, debug=True)
