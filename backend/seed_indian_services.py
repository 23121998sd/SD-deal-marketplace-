import requests
import json

# Backend URL
API_URL = "http://localhost:8001/api"

print("🚀 Creating SD DEAL - Indian Service Marketplace Data...\n")

# Create admin user
admin_token = None
try:
    admin_response = requests.post(f"{API_URL}/auth/login", json={
        "email": "admin@sddeal.com",
        "password": "admin123"
    })
    if admin_response.status_code == 200:
        admin_token = admin_response.json()['access_token']
        print("✅ Admin logged in")
    else:
        # Create admin
        admin_response = requests.post(f"{API_URL}/auth/register", json={
            "email": "admin@sddeal.com",
            "password": "admin123",
            "full_name": "SD Deal Admin",
            "phone": "+919876543210",
            "role": "admin"
        })
        admin_token = admin_response.json()['access_token']
        print("✅ Admin user created")
except Exception as e:
    print(f"⚠️ Admin: {e}")

if not admin_token:
    print("❌ Cannot proceed without admin token")
    exit(1)

# Indian-focused categories
categories = [
    {"name": "Home Cleaning", "description": "Deep cleaning aur sofa cleaning services", "icon": "🏠"},
    {"name": "Appliance Repair", "description": "AC service, Fridge, aur Washing Machine repair", "icon": "🔧"},
    {"name": "Electrician", "description": "Wiring, switchboard fixing, aur light installation", "icon": "⚡"},
    {"name": "Plumbing", "description": "Tap repair aur pipeline leakage solutions", "icon": "🚰"},
    {"name": "Personal Care", "description": "Home salon aur massage services", "icon": "💆"},
    {"name": "Pest Control", "description": "Termite aur general pest treatment", "icon": "🐛"},
    {"name": "Painting", "description": "Interior aur exterior painting", "icon": "🎨"},
    {"name": "Carpentry", "description": "Furniture repair aur custom work", "icon": "🪚"},
]

created_categories = []
for category in categories:
    try:
        response = requests.post(
            f"{API_URL}/categories",
            json=category,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code == 200:
            cat_data = response.json()
            created_categories.append(cat_data)
            print(f"✅ Created category: {category['name']}")
        else:
            print(f"⚠️ Category exists: {category['name']}")
            # Get existing
            cats_response = requests.get(f"{API_URL}/categories")
            all_cats = cats_response.json()
            for cat in all_cats:
                if cat['name'] == category['name']:
                    created_categories.append(cat)
                    break
    except Exception as e:
        print(f"❌ Failed {category['name']}: {e}")

print(f"\n📦 Total Categories: {len(created_categories)}\n")

# Create provider users with Indian names
providers = [
    {
        "email": "rajesh.kumar@provider.com",
        "password": "provider123",
        "full_name": "Rajesh Kumar",
        "phone": "+919876543211",
        "role": "provider"
    },
    {
        "email": "amit.sharma@provider.com",
        "password": "provider123",
        "full_name": "Amit Sharma",
        "phone": "+919876543212",
        "role": "provider"
    },
    {
        "email": "priya.singh@provider.com",
        "password": "provider123",
        "full_name": "Priya Singh",
        "phone": "+919876543213",
        "role": "provider"
    },
    {
        "email": "vikas.verma@provider.com",
        "password": "provider123",
        "full_name": "Vikas Verma",
        "phone": "+919876543214",
        "role": "provider"
    }
]

provider_tokens = []
for provider in providers:
    try:
        # Try login first
        login_response = requests.post(f"{API_URL}/auth/login", json={
            "email": provider['email'],
            "password": provider['password']
        })
        if login_response.status_code == 200:
            provider_tokens.append(login_response.json()['access_token'])
            print(f"✅ Provider logged in: {provider['full_name']}")
        else:
            # Register
            response = requests.post(f"{API_URL}/auth/register", json=provider)
            provider_tokens.append(response.json()['access_token'])
            print(f"✅ Provider created: {provider['full_name']}")
    except Exception as e:
        print(f"⚠️ Provider {provider['full_name']}: {e}")

print(f"\n👨‍🔧 Total Providers: {len(provider_tokens)}\n")

# Create comprehensive Indian services
services_data = []

if len(created_categories) >= 6:
    # Home Cleaning Services
    services_data.extend([
        {
            "title": "Deep Home Cleaning",
            "description": "Poora ghar ki deep cleaning - kitchen, bathroom, rooms, aur living area. Dust, stains, aur grime removal included.",
            "category_id": created_categories[0]['id'],
            "price": 1499.00,
            "duration_minutes": 240,
        },
        {
            "title": "Sofa Cleaning",
            "description": "Professional sofa aur upholstery cleaning. Stain removal, shampooing, aur vacuum cleaning.",
            "category_id": created_categories[0]['id'],
            "price": 799.00,
            "duration_minutes": 120,
        },
    ])
    
    # Appliance Repair Services
    services_data.extend([
        {
            "title": "AC Service & Repair",
            "description": "AC cleaning, gas refilling, aur repair service. Split aur window AC dono ke liye.",
            "category_id": created_categories[1]['id'],
            "price": 599.00,
            "duration_minutes": 90,
        },
        {
            "title": "Washing Machine Repair",
            "description": "Front load aur top load washing machine ki repair. Drum, motor, aur drainage issues fix karte hain.",
            "category_id": created_categories[1]['id'],
            "price": 499.00,
            "duration_minutes": 120,
        },
        {
            "title": "Refrigerator Repair",
            "description": "Fridge cooling problem, gas leakage, aur compressor repair. Single aur double door dono.",
            "category_id": created_categories[1]['id'],
            "price": 699.00,
            "duration_minutes": 150,
        },
    ])
    
    # Electrician Services
    services_data.extend([
        {
            "title": "House Wiring",
            "description": "Complete house wiring, rewiring, aur electrical fitting. Safe aur standard wiring guaranteed.",
            "category_id": created_categories[2]['id'],
            "price": 2999.00,
            "duration_minutes": 480,
        },
        {
            "title": "Switchboard Installation",
            "description": "New switchboard installation aur repair. Modular switches aur traditional dono.",
            "category_id": created_categories[2]['id'],
            "price": 399.00,
            "duration_minutes": 60,
        },
        {
            "title": "Light & Fan Installation",
            "description": "Ceiling fan, chandelier, aur decorative lights ka installation.",
            "category_id": created_categories[2]['id'],
            "price": 299.00,
            "duration_minutes": 45,
        },
    ])
    
    # Plumbing Services
    services_data.extend([
        {
            "title": "Tap Repair & Replacement",
            "description": "Leaky tap repair, washer replacement, aur new tap installation.",
            "category_id": created_categories[3]['id'],
            "price": 249.00,
            "duration_minutes": 60,
        },
        {
            "title": "Pipeline Leakage Fix",
            "description": "Water pipeline aur drainage pipe leak detection aur repair.",
            "category_id": created_categories[3]['id'],
            "price": 599.00,
            "duration_minutes": 120,
        },
    ])
    
    # Personal Care Services
    services_data.extend([
        {
            "title": "Home Salon for Women",
            "description": "Hair cut, facial, waxing, aur makeup services ghar par. Professional beautician.",
            "category_id": created_categories[4]['id'],
            "price": 1299.00,
            "duration_minutes": 180,
        },
        {
            "title": "Body Massage at Home",
            "description": "Relaxing full body massage ghar par. Swedish aur deep tissue massage available.",
            "category_id": created_categories[4]['id'],
            "price": 999.00,
            "duration_minutes": 90,
        },
    ])
    
    # Pest Control Services
    services_data.extend([
        {
            "title": "General Pest Control",
            "description": "Cockroaches, ants, lizards aur common pests ki treatment. Safe chemicals.",
            "category_id": created_categories[5]['id'],
            "price": 899.00,
            "duration_minutes": 120,
        },
        {
            "title": "Termite Treatment",
            "description": "Complete termite control aur prevention. Pre aur post construction treatment.",
            "category_id": created_categories[5]['id'],
            "price": 2499.00,
            "duration_minutes": 240,
        },
    ])

# Create services distributed among providers
for idx, service in enumerate(services_data):
    provider_token = provider_tokens[idx % len(provider_tokens)]
    try:
        response = requests.post(
            f"{API_URL}/services",
            json=service,
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        if response.status_code == 200:
            print(f"✅ Created service: {service['title']}")
        else:
            print(f"⚠️ Service failed: {service['title']} - {response.text}")
    except Exception as e:
        print(f"❌ Service error: {service['title']} - {e}")

# Create customer
try:
    customer_login = requests.post(f"{API_URL}/auth/login", json={
        "email": "customer@sddeal.com",
        "password": "customer123"
    })
    if customer_login.status_code != 200:
        customer_response = requests.post(f"{API_URL}/auth/register", json={
            "email": "customer@sddeal.com",
            "password": "customer123",
            "full_name": "Rahul Malhotra",
            "phone": "+919876543220",
            "role": "customer"
        })
        print("✅ Customer user created")
    else:
        print("✅ Customer logged in")
except Exception as e:
    print(f"⚠️ Customer: {e}")

print("\n" + "="*60)
print("🎉 SD DEAL - Indian Services Data Complete!")
print("="*60)
print("\n🔑 Test Accounts:")
print("Admin: admin@sddeal.com / admin123")
print("Provider: rajesh.kumar@provider.com / provider123")
print("Provider: amit.sharma@provider.com / provider123")
print("Provider: priya.singh@provider.com / provider123")
print("Provider: vikas.verma@provider.com / provider123")
print("Customer: customer@sddeal.com / customer123")
print("="*60)
print("\n📊 Database:")
print(f"✅ Categories: {len(created_categories)}")
print(f"✅ Providers: {len(provider_tokens)}")
print(f"✅ Services: {len(services_data)}")
print("="*60)
