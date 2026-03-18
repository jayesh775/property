"""
ApnaGhar - Property Listing Website
Flask Backend (app.py)
Author: Jayesh Gupta
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'apnaghar_secret_key_2026')

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

# Absolute path so DB works both locally and on Render
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apnaghar.db')

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionaries
    return conn


def init_db():
    """Initialize database with tables and sample data."""
    conn = get_db()
    c = conn.cursor()

    # ── propertyTable ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS propertyTable (
            propertyID   INTEGER PRIMARY KEY AUTOINCREMENT,
            Society      TEXT,
            Address      TEXT,
            City         TEXT,
            Price        INTEGER,
            Area         INTEGER,
            Type         TEXT,
            Bedrooms     INTEGER,
            Status       TEXT,
            Purpose      TEXT
        )
    ''')

    # ── customerTable ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS customerTable (
            customerID   INTEGER PRIMARY KEY AUTOINCREMENT,
            Name         TEXT,
            Surname      TEXT,
            Gender       TEXT,
            Age          INTEGER,
            Address      TEXT,
            Email        TEXT UNIQUE,
            Password     TEXT
        )
    ''')

    # ── shortlistedTable ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS shortlistedTable (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            customerID   INTEGER,
            propertyID   INTEGER,
            FOREIGN KEY (customerID) REFERENCES customerTable(customerID),
            FOREIGN KEY (propertyID) REFERENCES propertyTable(propertyID)
        )
    ''')

    # Insert sample data only if table is empty
    c.execute('SELECT COUNT(*) FROM propertyTable')
    if c.fetchone()[0] == 0:
        properties = [
            ('Green Valley',        'Sector 62, Noida, Uttar Pradesh 201309',       'Noida',    4500000,  900,  'Apartment',  2, 'Semi-Furnished',     'Sell'),
            ('Palm Residency',      'Dwarka Sector 12, Delhi 110075',               'Delhi',    6500000,  1200, 'Apartment',  3, 'Furnished',          'Sell'),
            ('Skyline Towers',      'Sector 45, Gurugram, Haryana 122003',          'Gurugram', 7200000,  1400, 'Apartment',  3, 'Unfurnished',        'Sell'),
            ('Ocean Heights',       'Andheri West, Mumbai, Maharashtra 400053',     'Mumbai',   15000000, 1100, 'Apartment',  2, 'Furnished',          'Sell'),
            ('Royal Farms',         'Sector 135, Noida, Uttar Pradesh 201304',      'Noida',    25000000, 3500, 'Farm House', 4, 'Semi-Furnished',     'Sell'),
            ('Lotus Greens',        'Mayur Vihar Phase 1, Delhi 110091',            'Delhi',    5500000,  1000, 'Apartment',  2, 'Unfurnished',        'Rent'),
            ('DLF Garden City',     'Sector 91, Gurugram, Haryana 122505',          'Gurugram', 8200000,  1600, 'House',      3, 'Semi-Furnished',     'Sell'),
            ('Sea Breeze',          'Bandra West, Mumbai, Maharashtra 400050',      'Mumbai',   22000000, 1500, 'Apartment',  3, 'Furnished',          'Rent'),
            ('Sunshine Apartments', 'Sector 76, Noida, Uttar Pradesh 201301',       'Noida',    4800000,  950,  'Apartment',  2, 'Under Construction', 'Sell'),
            ('Capital Residency',   'Karol Bagh, Delhi 110005',                     'Delhi',    6000000,  1150, 'House',      3, 'Semi-Furnished',     'Sell'),
            ('Emerald Hills',       'Sector 65, Gurugram, Haryana 122018',          'Gurugram', 9000000,  1700, 'Apartment',  4, 'Furnished',          'Sell'),
            ('Marine View',         'Colaba, Mumbai, Maharashtra 400005',            'Mumbai',   30000000, 1800, 'Apartment',  4, 'Furnished',          'Sell'),
            ('Golden Farms',        'Sector 150, Noida, Uttar Pradesh 201310',      'Noida',    27000000, 4000, 'Farm House', 5, 'Semi-Furnished',     'Sell'),
            ('Metro Heights',       'Laxmi Nagar, Delhi 110092',                    'Delhi',    5200000,  980,  'Apartment',  2, 'Unfurnished',        'Rent'),
            ('Signature Villas',    'Sector 57, Gurugram, Haryana 122011',          'Gurugram', 12500000, 2100, 'House',      4, 'Semi-Furnished',     'Sell'),
            ('Silver Sands',        'Juhu, Mumbai, Maharashtra 400049',              'Mumbai',   28000000, 1600, 'Apartment',  3, 'Furnished',          'Sell'),
            ('Elite Homes',         'Sector 50, Noida, Uttar Pradesh 201303',       'Noida',    7000000,  1300, 'House',      3, 'Semi-Furnished',     'Sell'),
            ('Heritage Apartments', 'Rohini Sector 9, Delhi 110085',                'Delhi',    5800000,  1050, 'Apartment',  2, 'Furnished',          'Rent'),
            ('Golf Course Residency','Sector 54, Gurugram, Haryana 122002',         'Gurugram', 14000000, 2000, 'Apartment',  4, 'Furnished',          'Sell'),
            ('Harbour View',        'Worli, Mumbai, Maharashtra 400018',             'Mumbai',   35000000, 1900, 'Apartment',  5, 'Furnished',          'Sell'),
            ('Green Meadows',       'Sector 137, Noida, Uttar Pradesh 201305',      'Noida',    4200000,  850,  'Apartment',  1, 'Unfurnished',        'Rent'),
            ('Urban Nest',          'Saket, Delhi 110017',                           'Delhi',    7500000,  1250, 'House',      3, 'Semi-Furnished',     'Sell'),
            ('Park View Residency', 'Sector 70, Gurugram, Haryana 122101',          'Gurugram', 6800000,  1350, 'Apartment',  3, 'Under Construction', 'Sell'),
            ('Blue Horizon',        'Powai, Mumbai, Maharashtra 400076',             'Mumbai',   24000000, 1450, 'Apartment',  3, 'Semi-Furnished',     'Sell'),
            ('Country Farms',       'Sector 168, Noida, Uttar Pradesh 201306',      'Noida',    26000000, 3700, 'Farm House', 5, 'Unfurnished',        'Sell'),
            ('City Square',         'Connaught Place, Delhi 110001',                'Delhi',    10000000, 1500, 'Apartment',  4, 'Furnished',          'Rent'),
            ('Palm Villas',         'Sector 82, Gurugram, Haryana 122004',          'Gurugram', 13500000, 2200, 'House',      4, 'Semi-Furnished',     'Sell'),
            ('Sunset Towers',       'Malad West, Mumbai, Maharashtra 400064',        'Mumbai',   18000000, 1400, 'Apartment',  3, 'Furnished',          'Sell'),
            ('Eco Heights',         'Sector 143, Noida, Uttar Pradesh 201307',      'Noida',    5000000,  1000, 'Apartment',  2, 'Under Construction', 'Sell'),
            ('Royal Enclave',       'Pitampura, Delhi 110034',                      'Delhi',    6200000,  1100, 'House',      3, 'Semi-Furnished',     'Rent'),
        ]
        c.executemany('''
            INSERT INTO propertyTable (Society, Address, City, Price, Area, Type, Bedrooms, Status, Purpose)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', properties)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────

def format_price(price):
    """Format price to Indian format (Lakhs/Crores)."""
    if price >= 10000000:
        return f"₹{price/10000000:.1f} Cr"
    elif price >= 100000:
        return f"₹{price/100000:.1f} L"
    return f"₹{price:,}"


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    """Homepage."""
    return render_template('index.html', user=session.get('user'))


@app.route('/bproperty')
def bproperty():
    """Buy property page."""
    conn = get_db()
    c = conn.cursor()

    # city & status are checkboxes → multiple values
    city      = request.args.getlist('city')
    status    = request.args.getlist('status')
    # type is a <select> → single value
    prop_type = request.args.get('type', '')
    # bedrooms is a radio → single value
    bedrooms  = request.args.get('bedrooms', '')
    min_price = request.args.get('min_price', 0, type=int)
    max_price = request.args.get('max_price', 999999999, type=int)

    # Build dynamic query
    query  = "SELECT * FROM propertyTable WHERE Purpose = 'Sell'"
    params = []

    if city:
        query += f" AND City IN ({','.join(['?']*len(city))})"
        params.extend(city)
    if prop_type:
        query += " AND Type = ?"
        params.append(prop_type)
    if bedrooms:
        query += " AND Bedrooms = ?"
        params.append(int(bedrooms))
    if status:
        query += f" AND Status IN ({','.join(['?']*len(status))})"
        params.extend(status)
    if min_price:
        query += " AND Price >= ?"
        params.append(min_price)
    if max_price < 999999999:
        query += " AND Price <= ?"
        params.append(max_price)

    c.execute(query, params)
    properties = c.fetchall()

    # Get unique filter values from DB
    c.execute("SELECT DISTINCT Type FROM propertyTable")
    types = [r[0] for r in c.fetchall()]
    c.execute("SELECT DISTINCT Status FROM propertyTable")
    statuses = [r[0] for r in c.fetchall()]

    conn.close()

    # Format prices
    props_list = []
    for p in properties:
        d = dict(p)
        d['formatted_price'] = format_price(d['Price'])
        props_list.append(d)

    return render_template('bproperty.html',
                           properties=props_list,
                           types=types,
                           statuses=statuses,
                           selected_cities=city,
                           selected_type=prop_type,
                           selected_bedrooms=bedrooms,
                           selected_statuses=status,
                           min_price=min_price,
                           max_price=max_price if max_price < 999999999 else 0,
                           user=session.get('user'))


@app.route('/tproperty')
def tproperty():
    """Tenant/Rent property page."""
    conn = get_db()
    c = conn.cursor()

    # city & status are checkboxes → multiple values
    city      = request.args.getlist('city')
    status    = request.args.getlist('status')
    # type is a <select> → single value
    prop_type = request.args.get('type', '')
    # bedrooms is a radio → single value
    bedrooms  = request.args.get('bedrooms', '')
    min_price = request.args.get('min_price', 0, type=int)
    max_price = request.args.get('max_price', 999999999, type=int)

    query  = "SELECT * FROM propertyTable WHERE Purpose = 'Rent'"
    params = []

    if city:
        query += f" AND City IN ({','.join(['?']*len(city))})"
        params.extend(city)
    if prop_type:
        query += " AND Type = ?"
        params.append(prop_type)
    if bedrooms:
        query += " AND Bedrooms = ?"
        params.append(int(bedrooms))
    if status:
        query += f" AND Status IN ({','.join(['?']*len(status))})"
        params.extend(status)
    if min_price:
        query += " AND Price >= ?"
        params.append(min_price)
    if max_price < 999999999:
        query += " AND Price <= ?"
        params.append(max_price)

    c.execute(query, params)
    properties = c.fetchall()

    c.execute("SELECT DISTINCT Type FROM propertyTable")
    types = [r[0] for r in c.fetchall()]
    c.execute("SELECT DISTINCT Status FROM propertyTable")
    statuses = [r[0] for r in c.fetchall()]

    conn.close()

    props_list = []
    for p in properties:
        d = dict(p)
        d['formatted_price'] = format_price(d['Price'])
        props_list.append(d)

    return render_template('tproperty.html',
                           properties=props_list,
                           types=types,
                           statuses=statuses,
                           selected_cities=city,
                           selected_type=prop_type,
                           selected_bedrooms=bedrooms,
                           selected_statuses=status,
                           min_price=min_price,
                           max_price=max_price if max_price < 999999999 else 0,
                           user=session.get('user'))


@app.route('/map')
def map_view():
    """Map view page — redesigned with AreaAvgPrice heatmap."""
    return render_template('map.html', user=session.get('user'))


@app.route('/api/area_prices')
def area_prices():
    """Return all areas + avg prices for a given city."""
    city = request.args.get('city', 'Delhi')
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'SELECT Area, AveragePrice FROM AreaAvgPrice WHERE City = ? ORDER BY Area',
        (city,)
    )
    rows = c.fetchall()
    conn.close()
    return jsonify({
        'city': city,
        'areas': [{'area': r[0], 'price': r[1]} for r in rows]
    })


@app.route('/flatmate')
def flatmate():
    """Find flatmate page."""
    return render_template('flatmate.html', user=session.get('user'))


@app.route('/form', methods=['GET', 'POST'])
def form():
    """List a property page."""
    if request.method == 'POST':
        data = request.get_json()
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO propertyTable (Society, Address, City, Price, Area, Type, Bedrooms, Status, Purpose)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['society'], data['address'], data['city'],
            int(data['price']), int(data['area']),
            data['type'], int(data['bedrooms']),
            data['status'], data['purpose']
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Property listed successfully!'})
    return render_template('form.html', user=session.get('user'))


@app.route('/price_recommend')
def price_recommend():
    """Price recommendation page."""
    return render_template('priceRecommend.html', user=session.get('user'))


# ─────────────────────────────────────────────
# AUTH ROUTES (API)
# ─────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM customerTable WHERE Email = ? AND Password = ?',
              (data['email'], data['password']))
    user = c.fetchone()
    conn.close()
    if user:
        session['user'] = {
            'id': user['customerID'],
            'name': user['Name'],
            'surname': user['Surname'],
            'email': user['Email']
        }
        return jsonify({'success': True, 'name': user['Name']})
    return jsonify({'success': False, 'message': 'Invalid email or password'})


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO customerTable (Name, Surname, Gender, Age, Address, Email, Password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['surname'], data['gender'],
              int(data['age']), data['address'], data['email'], data['password']))
        conn.commit()
        user_id = c.lastrowid
        session['user'] = {
            'id': user_id,
            'name': data['name'],
            'surname': data['surname'],
            'email': data['email']
        }
        conn.close()
        return jsonify({'success': True, 'name': data['name']})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Email already registered'})


@app.route('/api/logout')
def logout():
    session.pop('user', None)
    return jsonify({'success': True})


@app.route('/api/profile')
def profile():
    if 'user' not in session:
        return jsonify({'success': False})
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM customerTable WHERE customerID = ?', (session['user']['id'],))
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({'success': True, 'user': dict(user)})
    return jsonify({'success': False})


@app.route('/api/shortlist', methods=['POST'])
def shortlist():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    # Check if already shortlisted
    c.execute('SELECT * FROM shortlistedTable WHERE customerID = ? AND propertyID = ?',
              (session['user']['id'], data['propertyID']))
    existing = c.fetchone()
    if existing:
        c.execute('DELETE FROM shortlistedTable WHERE customerID = ? AND propertyID = ?',
                  (session['user']['id'], data['propertyID']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'action': 'removed'})
    c.execute('INSERT INTO shortlistedTable (customerID, propertyID) VALUES (?, ?)',
              (session['user']['id'], data['propertyID']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'action': 'added'})


@app.route('/api/shortlisted')
def get_shortlisted():
    if 'user' not in session:
        return jsonify({'success': False})
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT p.*, s.id as shortlist_id
        FROM propertyTable p
        JOIN shortlistedTable s ON p.propertyID = s.propertyID
        WHERE s.customerID = ?
    ''', (session['user']['id'],))
    props = [dict(r) for r in c.fetchall()]
    conn.close()
    for p in props:
        p['formatted_price'] = format_price(p['Price'])
    return jsonify({'success': True, 'properties': props})


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
