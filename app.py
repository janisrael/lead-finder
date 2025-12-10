from flask import Flask, request, jsonify, send_from_directory
import threading
import sqlite3
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DB_PATH = os.path.abspath("places.db")


# ------------------ DATABASE SETUP ------------------ #
def init_db():
    conn = sqlite3.connect(DB_PATH)
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
            status TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def clear_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM places')
    conn.commit()
    conn.close()


def insert_place(place):
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()


# ------------------ GOOGLE PLACES ------------------ #
def get_place_details(api_key, place_id):
    try:
        url = 'https://maps.googleapis.com/maps/api/place/details/json'
        params = {
            'key': api_key,
            'place_id': place_id,
            'fields': 'website,formatted_phone_number'
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        result = res.json().get('result', {})
        return result.get('website', ''), result.get('formatted_phone_number', '')
    except:
        return '', ''


def crawl_places_async(api_key, location, radius, types, has_website, keyword=''):
    def crawl():
        for type_ in types:
            print(f"[CRAWL] {type_}")
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            params = {
                'key': api_key,
                'location': location,
                'radius': radius,
                'keyword': type_  # PHP uses 'keyword' not 'type'
            }
            if keyword:
                params['keyword'] = keyword

            while True:
                try:
                    res = requests.get(url, params=params, timeout=30)
                    res.raise_for_status()
                    data = res.json()
                    
                    # Check for API errors
                    if data.get('status') == 'REQUEST_DENIED':
                        print(f"[ERROR] API Request Denied: {data.get('error_message', 'Unknown error')}")
                        break
                    elif data.get('status') == 'OVER_QUERY_LIMIT':
                        print(f"[ERROR] API Quota Exceeded")
                        break
                    elif data.get('status') != 'OK' and data.get('status') != 'ZERO_RESULTS':
                        print(f"[ERROR] API Error: {data.get('status')} - {data.get('error_message', '')}")
                        break

                    for place in data.get('results', []):
                        name = place.get('name')
                        address = place.get('vicinity')
                        place_id = place.get('place_id')
                        rating = place.get('rating')
                        types_list = place.get('types', [])
                        status = place.get('business_status', '')
                        website, phone = get_place_details(api_key, place_id)

                        include = (
                            (has_website == 'yes' and website) or
                            (has_website == 'no' and not website) or
                            (has_website == 'both')
                        )

                        if include:
                            insert_place({
                                'name': name,
                                'address': address,
                                'phone': phone,
                                'website': website,
                                'rating': rating,
                                'types': types_list,
                                'status': status
                            })

                    if 'next_page_token' in data:
                        time.sleep(2)
                        params['pagetoken'] = data['next_page_token']
                    else:
                        break

                except Exception as e:
                    print(f"[ERROR] {e}")
                    break

    thread = threading.Thread(target=crawl)
    thread.start()


# ------------------ API ROUTES ------------------ #

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/app.js')
def app_js():
    return send_from_directory('.', 'app.js')

@app.route('/favicon.svg')
def favicon_svg():
    return send_from_directory('.', 'favicon.svg', mimetype='image/svg+xml')

@app.route('/favicon.ico')
def favicon_ico():
    return send_from_directory('.', 'favicon.ico', mimetype='image/x-icon')

@app.route('/test')
def test():
    return send_from_directory('.', 'test_frontend.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'lead-finder',
        'version': '1.0'
    })

@app.route('/crawl', methods=['GET'])
def crawl_endpoint():
    init_db()
    clear_db()

    api_key = os.environ.get('GOOGLE_PLACES_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'Google Places API key not configured'}), 500
    
    location = request.args.get('location', '50.0405,-110.6766')
    radius_km = float(request.args.get('radius', 20))
    radius = min(int(radius_km * 1000), 50000)  # Convert KM to meters, max 50km like PHP
    keyword = request.args.get('keyword', '')
    types = request.args.get('types', 'restaurant').split(',')
    has_website = request.args.get('has_website', 'both')

    crawl_places_async(api_key, location, radius, types, has_website, keyword)

    return jsonify({"status": "started"})


@app.route('/stream', methods=['GET'])
def stream_results():
    last_id = int(request.args.get('last_id', 0))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM places WHERE id > ? ORDER BY id ASC", (last_id,))
    rows = cur.fetchall()
    conn.close()

    new_results = []
    max_id = last_id
    for row in rows:
        new_results.append({
            'id': row['id'],
            'name': row['name'],
            'address': row['address'],
            'phone': row['phone'],
            'website': row['website'],
            'rating': row['rating'],
            'types': row['types'].split(','),
            'status': row['status']
        })
        if row['id'] > max_id:
            max_id = row['id']

    return jsonify({'last_id': max_id, 'results': new_results})


# ------------------ MAIN ------------------ #

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 6005))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
