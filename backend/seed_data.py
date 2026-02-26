import requests
import json

# Backend URL
API_URL = "http://localhost:8001/api"

# Create admin user
try:
    admin_response = requests.post(f"{API_URL}/auth/register", json={
        "email": "admin@servicemarket.com",
        "password": "admin123",
        "full_name": "Admin User",
        "phone": "+1234567890",
        "role": "admin"
    })
    admin_data = admin_response.json()
    admin_token = admin_data['access_token']
    print("✅ Admin user created")
except Exception as e:
    print(f"Admin creation: {e}")

# Create categories
categories = [
    {"name": "Home Cleaning", "description": "Professional home cleaning services", "icon": "🏠"},
    {"name": "Plumbing", "description": "Plumbing repairs and installations", "icon": "🔧"},
    {"name": "Electrical", "description": "Electrical repairs and installations", "icon": "⚡"},
    {"name": "Carpentry", "description": "Custom carpentry and furniture", "icon": "🪚"},
    {"name": "Painting", "description": "Interior and exterior painting", "icon": "🎨"},
    {"name": "Gardening", "description": "Garden maintenance and landscaping", "icon": "🌱"},
    {"name": "Appliance Repair", "description": "Repair of home appliances", "icon": "🔨"},
    {"name": "Pest Control", "description": "Pest elimination services", "icon": "🐛"},
    {"name": "Moving", "description": "Moving and packing services", "icon": "📦"},
    {"name": "Beauty & Spa", "description": "Beauty treatments at home", "icon": "💅"},
    {"name": "Tutoring", "description": "Private tutoring services", "icon": "📚"},
    {"name": "IT Support", "description": "Computer and tech support", "icon": "💻"}
]

try:
    for category in categories:
        response = requests.post(
            f"{API_URL}/categories",
            json=category,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code == 200:
            print(f"✅ Created category: {category['name']}")
        else:
            print(f"❌ Failed to create {category['name']}: {response.text}")
except Exception as e:
    print(f"Category creation error: {e}")

# Create provider user
try:
    provider_response = requests.post(f"{API_URL}/auth/register", json={
        "email": "provider@test.com",
        "password": "provider123",
        "full_name": "John Provider",
        "phone": "+1234567891",
        "role": "provider"
    })
    provider_data = provider_response.json()
    provider_token = provider_data['access_token']
    provider_id = provider_data['user']['id']
    print("✅ Provider user created")
    
    # Get first category
    categories_response = requests.get(f"{API_URL}/categories")
    categories_list = categories_response.json()
    
    if categories_list:
        # Create some services
        services = [
            {
                "title": "Deep Home Cleaning",
                "description": "Complete deep cleaning of your home including all rooms, kitchen, and bathrooms",
                "category_id": categories_list[0]['id'],
                "price": 89.99,
                "duration_minutes": 180,
                "images": []
            },
            {
                "title": "Kitchen Plumbing Repair",
                "description": "Fix leaky faucets, clogged drains, and other kitchen plumbing issues",
                "category_id": categories_list[1]['id'],
                "price": 75.00,
                "duration_minutes": 120,
                "images": []
            },
            {
                "title": "Electrical Outlet Installation",
                "description": "Install new electrical outlets and switches safely",
                "category_id": categories_list[2]['id'],
                "price": 65.00,
                "duration_minutes": 90,
                "images": []
            }
        ]
        
        for service in services:
            response = requests.post(
                f"{API_URL}/services",
                json=service,
                headers={"Authorization": f"Bearer {provider_token}"}
            )
            if response.status_code == 200:
                print(f"✅ Created service: {service['title']}")
            else:
                print(f"❌ Failed to create {service['title']}: {response.text}")
    
except Exception as e:
    print(f"Provider/Services creation error: {e}")

# Create customer user
try:
    customer_response = requests.post(f"{API_URL}/auth/register", json={
        "email": "customer@test.com",
        "password": "customer123",
        "full_name": "Jane Customer",
        "phone": "+1234567892",
        "role": "customer"
    })
    print("✅ Customer user created")
except Exception as e:
    print(f"Customer creation: {e}")

print("\n" + "="*50)
print("🎉 Seed data creation complete!")
print("="*50)
print("\nTest Accounts:")
print("Admin: admin@servicemarket.com / admin123")
print("Provider: provider@test.com / provider123")
print("Customer: customer@test.com / customer123")
print("="*50)
