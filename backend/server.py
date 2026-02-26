from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import socketio
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import random
import aiofiles
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-2025")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))

# Stripe
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# Create Socket.IO async server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# ======================
# Models
# ======================

class UserRole:
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"

class BookingStatus:
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TransactionType:
    BOOKING_PAYMENT = "booking_payment"
    COMMISSION = "commission"
    PAYOUT = "payout"
    REFUND = "refund"

class TransactionStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class WithdrawalStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: str = UserRole.CUSTOMER

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True
    is_verified: bool = False
    wallet_balance: float = 0.0
    profile_image: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    location: Optional[Dict[str, float]] = None  # {"lat": 0.0, "lng": 0.0}
    rating: float = 0.0
    total_reviews: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

class UserResponse(User):
    pass

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Category Models
class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

# Service Models
class ServiceBase(BaseModel):
    title: str
    description: str
    category_id: str
    price: float
    duration_minutes: Optional[int] = 60
    images: Optional[List[str]] = []

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str
    is_active: bool = True
    rating: float = 0.0
    total_bookings: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

class ServiceWithProvider(Service):
    provider: Optional[UserResponse] = None
    category: Optional[Category] = None

# Booking Models
class BookingCreate(BaseModel):
    service_id: str
    booking_date: str  # YYYY-MM-DD
    booking_time: str  # HH:MM
    notes: Optional[str] = None
    customer_address: str

class Booking(BookingCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    provider_id: str
    status: str = BookingStatus.PENDING
    amount: float
    commission: float
    otp: Optional[str] = None
    payment_session_id: Optional[str] = None
    payment_status: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

class BookingWithDetails(Booking):
    service: Optional[Service] = None
    customer: Optional[UserResponse] = None
    provider: Optional[UserResponse] = None

# Review Models
class ReviewRatings(BaseModel):
    behavior: int = Field(..., ge=1, le=5)
    punctuality: int = Field(..., ge=1, le=5)
    quality: int = Field(..., ge=1, le=5)
    value_for_money: int = Field(..., ge=1, le=5)

class ReviewCreate(BaseModel):
    booking_id: str
    ratings: ReviewRatings
    comment: Optional[str] = None
    images: Optional[List[str]] = []

class Review(ReviewCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    provider_id: str
    service_id: str
    overall_rating: float
    provider_reply: Optional[str] = None
    helpful_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

class ReviewWithDetails(Review):
    customer: Optional[UserResponse] = None

# Chat Models
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str
    receiver_id: str
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

class MessageCreate(BaseModel):
    receiver_id: str
    message: str
    booking_id: Optional[str] = None

# Transaction Models
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    booking_id: Optional[str] = None
    type: str
    amount: float
    status: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

# Withdrawal Models
class WithdrawalCreate(BaseModel):
    amount: float
    bank_account_number: str
    bank_name: str
    account_holder_name: str

class Withdrawal(WithdrawalCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str
    status: str = WithdrawalStatus.PENDING
    admin_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    model_config = ConfigDict(extra="ignore")

# Payment Transaction Models
class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    booking_id: str
    amount: float
    currency: str
    payment_status: str = "pending"
    metadata: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(extra="ignore")

# ======================
# Helper Functions
# ======================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def calculate_overall_rating(ratings: ReviewRatings) -> float:
    return (ratings.behavior + ratings.punctuality + ratings.quality + ratings.value_for_money) / 4

# ======================
# Socket.IO Events
# ======================

connected_users = {}

@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")
    # Remove from connected users
    user_id_to_remove = None
    for user_id, socket_id in connected_users.items():
        if socket_id == sid:
            user_id_to_remove = user_id
            break
    if user_id_to_remove:
        del connected_users[user_id_to_remove]

@sio.event
async def register_user(sid, data):
    """Register user's socket ID for real-time messaging"""
    user_id = data.get('user_id')
    if user_id:
        connected_users[user_id] = sid
        print(f"User {user_id} registered with socket {sid}")

@sio.event
async def send_message(sid, data):
    """Send a message to another user"""
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    booking_id = data.get('booking_id')
    
    # Create conversation ID
    conv_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
    if booking_id:
        conv_id = f"{conv_id}_{booking_id}"
    
    # Save message to database
    message = Message(
        conversation_id=conv_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message_text
    )
    
    message_dict = message.model_dump()
    message_dict['created_at'] = message_dict['created_at'].isoformat()
    await db.messages.insert_one(message_dict)
    
    # Send to receiver if online
    receiver_socket = connected_users.get(receiver_id)
    if receiver_socket:
        await sio.emit('new_message', message_dict, room=receiver_socket)
    
    # Confirm to sender
    await sio.emit('message_sent', message_dict, room=sid)

@sio.event
async def mark_read(sid, data):
    """Mark messages as read"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    await db.messages.update_many(
        {"conversation_id": conversation_id, "receiver_id": user_id},
        {"$set": {"is_read": True}}
    )

# ======================
# API Routes
# ======================

@api_router.get("/")
async def root():
    return {"message": "Service Marketplace API", "version": "1.0.0"}

# ==================
# Auth Routes
# ==================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_obj = User(
        **user.model_dump(exclude={"password"})
    )
    user_dict = user_obj.model_dump()
    user_dict['hashed_password'] = hash_password(user.password)
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token(data={"sub": user_obj.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_obj
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    # Find user
    user_doc = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user_doc['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Convert datetime strings back to datetime objects
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    user = User(**user_doc)
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.put("/auth/profile", response_model=UserResponse)
async def update_profile(updates: Dict, current_user: User = Depends(get_current_user)):
    # Remove sensitive fields
    updates.pop('id', None)
    updates.pop('email', None)
    updates.pop('role', None)
    updates.pop('wallet_balance', None)
    updates.pop('hashed_password', None)
    
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": updates}
    )
    
    updated_user = await db.users.find_one({"id": current_user.id}, {"_id": 0})
    if isinstance(updated_user['created_at'], str):
        updated_user['created_at'] = datetime.fromisoformat(updated_user['created_at'])
    
    return User(**updated_user)

# ==================
# Category Routes
# ==================

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    categories = await db.categories.find({}, {"_id": 0}).to_list(100)
    for cat in categories:
        if isinstance(cat['created_at'], str):
            cat['created_at'] = datetime.fromisoformat(cat['created_at'])
    return categories

@api_router.post("/categories", response_model=Category)
async def create_category(category: CategoryCreate, current_user: User = Depends(get_current_user)):
    # Only admin can create categories
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create categories")
    
    cat_obj = Category(**category.model_dump())
    cat_dict = cat_obj.model_dump()
    cat_dict['created_at'] = cat_dict['created_at'].isoformat()
    
    await db.categories.insert_one(cat_dict)
    return cat_obj

# ==================
# Service Routes
# ==================

@api_router.post("/services", response_model=Service)
async def create_service(service: ServiceCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers can create services")
    
    service_obj = Service(**service.model_dump(), provider_id=current_user.id)
    service_dict = service_obj.model_dump()
    service_dict['created_at'] = service_dict['created_at'].isoformat()
    
    await db.services.insert_one(service_dict)
    return service_obj

@api_router.get("/services", response_model=List[ServiceWithProvider])
async def get_services(
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[str] = "created_at"
):
    # Build query
    query = {"is_active": True}
    if category_id:
        query["category_id"] = category_id
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if min_price is not None:
        query["price"] = {"$gte": min_price}
    if max_price is not None:
        if "price" in query:
            query["price"]["$lte"] = max_price
        else:
            query["price"] = {"$lte": max_price}
    if min_rating is not None:
        query["rating"] = {"$gte": min_rating}
    
    # Sorting
    sort_field = sort_by
    sort_order = -1  # Descending
    
    services = await db.services.find(query, {"_id": 0}).sort(sort_field, sort_order).to_list(100)
    
    # Enrich with provider and category data
    result = []
    for service in services:
        if isinstance(service['created_at'], str):
            service['created_at'] = datetime.fromisoformat(service['created_at'])
        
        provider = await db.users.find_one({"id": service['provider_id']}, {"_id": 0, "hashed_password": 0})
        if provider and isinstance(provider.get('created_at'), str):
            provider['created_at'] = datetime.fromisoformat(provider['created_at'])
        
        category = await db.categories.find_one({"id": service['category_id']}, {"_id": 0})
        if category and isinstance(category.get('created_at'), str):
            category['created_at'] = datetime.fromisoformat(category['created_at'])
        
        service['provider'] = provider
        service['category'] = category
        result.append(service)
    
    return result

@api_router.get("/services/{service_id}", response_model=ServiceWithProvider)
async def get_service(service_id: str):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if isinstance(service['created_at'], str):
        service['created_at'] = datetime.fromisoformat(service['created_at'])
    
    provider = await db.users.find_one({"id": service['provider_id']}, {"_id": 0, "hashed_password": 0})
    if provider and isinstance(provider.get('created_at'), str):
        provider['created_at'] = datetime.fromisoformat(provider['created_at'])
    
    category = await db.categories.find_one({"id": service['category_id']}, {"_id": 0})
    if category and isinstance(category.get('created_at'), str):
        category['created_at'] = datetime.fromisoformat(category['created_at'])
    
    service['provider'] = provider
    service['category'] = category
    
    return service

@api_router.get("/my-services", response_model=List[Service])
async def get_my_services(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers can access this")
    
    services = await db.services.find({"provider_id": current_user.id}, {"_id": 0}).to_list(100)
    for service in services:
        if isinstance(service['created_at'], str):
            service['created_at'] = datetime.fromisoformat(service['created_at'])
    return services

@api_router.put("/services/{service_id}", response_model=Service)
async def update_service(service_id: str, updates: Dict, current_user: User = Depends(get_current_user)):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service['provider_id'] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updates.pop('id', None)
    updates.pop('provider_id', None)
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.services.update_one({"id": service_id}, {"$set": updates})
    
    updated_service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if isinstance(updated_service['created_at'], str):
        updated_service['created_at'] = datetime.fromisoformat(updated_service['created_at'])
    
    return Service(**updated_service)

@api_router.delete("/services/{service_id}")
async def delete_service(service_id: str, current_user: User = Depends(get_current_user)):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service['provider_id'] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.services.update_one({"id": service_id}, {"$set": {"is_active": False}})
    return {"message": "Service deleted successfully"}

# ==================
# Booking Routes
# ==================

@api_router.post("/bookings", response_model=Dict)
async def create_booking(booking: BookingCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can create bookings")
    
    # Get service
    service = await db.services.find_one({"id": booking.service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Calculate commission (15%)
    commission = service['price'] * 0.15
    
    # Create booking
    booking_obj = Booking(
        **booking.model_dump(),
        customer_id=current_user.id,
        provider_id=service['provider_id'],
        amount=service['price'],
        commission=commission
    )
    
    booking_dict = booking_obj.model_dump()
    booking_dict['created_at'] = booking_dict['created_at'].isoformat()
    booking_dict['updated_at'] = booking_dict['updated_at'].isoformat()
    
    await db.bookings.insert_one(booking_dict)
    
    return {"booking_id": booking_obj.id, "amount": service['price']}

@api_router.post("/bookings/{booking_id}/checkout")
async def create_checkout_session(booking_id: str, origin_url: str, current_user: User = Depends(get_current_user)):
    # Get booking
    booking = await db.bookings.find_one({"id": booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking['customer_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Initialize Stripe
    webhook_url = f"{origin_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session
    success_url = f"{origin_url}/booking-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/booking/{booking_id}"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(booking['amount']),
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"booking_id": booking_id, "customer_id": current_user.id}
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Save payment transaction
    payment_txn = PaymentTransaction(
        session_id=session.session_id,
        user_id=current_user.id,
        booking_id=booking_id,
        amount=float(booking['amount']),
        currency="usd",
        payment_status="pending",
        metadata={"booking_id": booking_id}
    )
    
    payment_dict = payment_txn.model_dump()
    payment_dict['created_at'] = payment_dict['created_at'].isoformat()
    payment_dict['updated_at'] = payment_dict['updated_at'].isoformat()
    
    await db.payment_transactions.insert_one(payment_dict)
    
    # Update booking
    await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {"payment_session_id": session.session_id}}
    )
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/bookings/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, current_user: User = Depends(get_current_user)):
    # Initialize Stripe
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    # Get status
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update payment transaction
    payment_txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if payment_txn and payment_txn['payment_status'] != "paid":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "payment_status": status.payment_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Update booking
        if status.payment_status == "paid":
            booking_id = payment_txn['booking_id']
            await db.bookings.update_one(
                {"id": booking_id},
                {"$set": {"payment_status": "paid", "status": BookingStatus.PENDING}}
            )
    
    return status.model_dump()

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update payment transaction
        await db.payment_transactions.update_one(
            {"session_id": webhook_response.session_id},
            {"$set": {
                "payment_status": webhook_response.payment_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Update booking if paid
        if webhook_response.payment_status == "paid":
            payment_txn = await db.payment_transactions.find_one({"session_id": webhook_response.session_id}, {"_id": 0})
            if payment_txn:
                await db.bookings.update_one(
                    {"id": payment_txn['booking_id']},
                    {"$set": {"payment_status": "paid"}}
                )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/bookings", response_model=List[BookingWithDetails])
async def get_bookings(current_user: User = Depends(get_current_user)):
    query = {}
    if current_user.role == UserRole.CUSTOMER:
        query["customer_id"] = current_user.id
    elif current_user.role == UserRole.PROVIDER:
        query["provider_id"] = current_user.id
    
    bookings = await db.bookings.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    # Enrich with details
    result = []
    for booking in bookings:
        if isinstance(booking['created_at'], str):
            booking['created_at'] = datetime.fromisoformat(booking['created_at'])
        if isinstance(booking['updated_at'], str):
            booking['updated_at'] = datetime.fromisoformat(booking['updated_at'])
        
        service = await db.services.find_one({"id": booking['service_id']}, {"_id": 0})
        if service and isinstance(service.get('created_at'), str):
            service['created_at'] = datetime.fromisoformat(service['created_at'])
        
        customer = await db.users.find_one({"id": booking['customer_id']}, {"_id": 0, "hashed_password": 0})
        if customer and isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
        
        provider = await db.users.find_one({"id": booking['provider_id']}, {"_id": 0, "hashed_password": 0})
        if provider and isinstance(provider.get('created_at'), str):
            provider['created_at'] = datetime.fromisoformat(provider['created_at'])
        
        booking['service'] = service
        booking['customer'] = customer
        booking['provider'] = provider
        result.append(booking)
    
    return result

@api_router.get("/bookings/{booking_id}", response_model=BookingWithDetails)
async def get_booking(booking_id: str, current_user: User = Depends(get_current_user)):
    booking = await db.bookings.find_one({"id": booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking['customer_id'] != current_user.id and booking['provider_id'] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if isinstance(booking['created_at'], str):
        booking['created_at'] = datetime.fromisoformat(booking['created_at'])
    if isinstance(booking['updated_at'], str):
        booking['updated_at'] = datetime.fromisoformat(booking['updated_at'])
    
    service = await db.services.find_one({"id": booking['service_id']}, {"_id": 0})
    if service and isinstance(service.get('created_at'), str):
        service['created_at'] = datetime.fromisoformat(service['created_at'])
    
    customer = await db.users.find_one({"id": booking['customer_id']}, {"_id": 0, "hashed_password": 0})
    if customer and isinstance(customer.get('created_at'), str):
        customer['created_at'] = datetime.fromisoformat(customer['created_at'])
    
    provider = await db.users.find_one({"id": booking['provider_id']}, {"_id": 0, "hashed_password": 0})
    if provider and isinstance(provider.get('created_at'), str):
        provider['created_at'] = datetime.fromisoformat(provider['created_at'])
    
    booking['service'] = service
    booking['customer'] = customer
    booking['provider'] = provider
    
    return booking

@api_router.put("/bookings/{booking_id}/status")
async def update_booking_status(booking_id: str, status: str, otp: Optional[str] = None, current_user: User = Depends(get_current_user)):
    booking = await db.bookings.find_one({"id": booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Status transitions
    if status == BookingStatus.ACCEPTED:
        if current_user.role != UserRole.PROVIDER or booking['provider_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Only provider can accept booking")
    
    elif status == BookingStatus.IN_PROGRESS:
        if current_user.role != UserRole.PROVIDER or booking['provider_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Only provider can start booking")
        # Generate OTP
        new_otp = generate_otp()
        await db.bookings.update_one({"id": booking_id}, {"$set": {"otp": new_otp}})
        return {"message": "OTP generated", "otp": new_otp}
    
    elif status == BookingStatus.COMPLETED:
        if current_user.role != UserRole.PROVIDER or booking['provider_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Only provider can complete booking")
        # Verify OTP
        if not otp or booking.get('otp') != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        # Transfer money to provider wallet (amount - commission)
        provider_amount = booking['amount'] - booking['commission']
        await db.users.update_one(
            {"id": booking['provider_id']},
            {"$inc": {"wallet_balance": provider_amount}}
        )
        
        # Create transaction
        transaction = Transaction(
            user_id=booking['provider_id'],
            booking_id=booking_id,
            type=TransactionType.BOOKING_PAYMENT,
            amount=provider_amount,
            status=TransactionStatus.COMPLETED,
            description=f"Payment for booking {booking_id}"
        )
        txn_dict = transaction.model_dump()
        txn_dict['created_at'] = txn_dict['created_at'].isoformat()
        await db.transactions.insert_one(txn_dict)
    
    elif status == BookingStatus.CANCELLED:
        if booking['customer_id'] != current_user.id and booking['provider_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update status
    await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Booking status updated", "status": status}

# ==================
# Review Routes
# ==================

@api_router.post("/reviews", response_model=Review)
async def create_review(review: ReviewCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can create reviews")
    
    # Get booking
    booking = await db.bookings.find_one({"id": review.booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking['customer_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if booking['status'] != BookingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed bookings")
    
    # Check if already reviewed
    existing_review = await db.reviews.find_one({"booking_id": review.booking_id}, {"_id": 0})
    if existing_review:
        raise HTTPException(status_code=400, detail="Booking already reviewed")
    
    # Calculate overall rating
    overall_rating = calculate_overall_rating(review.ratings)
    
    review_obj = Review(
        **review.model_dump(),
        customer_id=current_user.id,
        provider_id=booking['provider_id'],
        service_id=booking['service_id'],
        overall_rating=overall_rating
    )
    
    review_dict = review_obj.model_dump()
    review_dict['created_at'] = review_dict['created_at'].isoformat()
    
    await db.reviews.insert_one(review_dict)
    
    # Update provider rating
    provider_reviews = await db.reviews.find({"provider_id": booking['provider_id']}, {"_id": 0}).to_list(1000)
    if provider_reviews:
        avg_rating = sum(r['overall_rating'] for r in provider_reviews) / len(provider_reviews)
        await db.users.update_one(
            {"id": booking['provider_id']},
            {"$set": {"rating": avg_rating, "total_reviews": len(provider_reviews)}}
        )
    
    # Update service rating
    service_reviews = await db.reviews.find({"service_id": booking['service_id']}, {"_id": 0}).to_list(1000)
    if service_reviews:
        avg_rating = sum(r['overall_rating'] for r in service_reviews) / len(service_reviews)
        await db.services.update_one(
            {"id": booking['service_id']},
            {"$set": {"rating": avg_rating}}
        )
    
    return review_obj

@api_router.get("/reviews/service/{service_id}", response_model=List[ReviewWithDetails])
async def get_service_reviews(service_id: str):
    reviews = await db.reviews.find({"service_id": service_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    result = []
    for review in reviews:
        if isinstance(review['created_at'], str):
            review['created_at'] = datetime.fromisoformat(review['created_at'])
        
        customer = await db.users.find_one({"id": review['customer_id']}, {"_id": 0, "hashed_password": 0})
        if customer and isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
        
        review['customer'] = customer
        result.append(review)
    
    return result

@api_router.get("/reviews/provider/{provider_id}", response_model=List[ReviewWithDetails])
async def get_provider_reviews(provider_id: str):
    reviews = await db.reviews.find({"provider_id": provider_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    result = []
    for review in reviews:
        if isinstance(review['created_at'], str):
            review['created_at'] = datetime.fromisoformat(review['created_at'])
        
        customer = await db.users.find_one({"id": review['customer_id']}, {"_id": 0, "hashed_password": 0})
        if customer and isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
        
        review['customer'] = customer
        result.append(review)
    
    return result

@api_router.put("/reviews/{review_id}/reply")
async def reply_to_review(review_id: str, reply: str, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers can reply to reviews")
    
    review = await db.reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review['provider_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.reviews.update_one(
        {"id": review_id},
        {"$set": {"provider_reply": reply}}
    )
    
    return {"message": "Reply added successfully"}

# ==================
# Chat Routes
# ==================

@api_router.get("/messages/{conversation_id}", response_model=List[Message])
async def get_conversation_messages(conversation_id: str, current_user: User = Depends(get_current_user)):
    messages = await db.messages.find({"conversation_id": conversation_id}, {"_id": 0}).sort("created_at", 1).to_list(500)
    
    for msg in messages:
        if isinstance(msg['created_at'], str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return messages

@api_router.get("/conversations", response_model=List[Dict])
async def get_conversations(current_user: User = Depends(get_current_user)):
    # Get all conversations for current user
    messages = await db.messages.find(
        {"$or": [{"sender_id": current_user.id}, {"receiver_id": current_user.id}]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    # Group by conversation
    conversations = {}
    for msg in messages:
        conv_id = msg['conversation_id']
        if conv_id not in conversations:
            other_user_id = msg['receiver_id'] if msg['sender_id'] == current_user.id else msg['sender_id']
            other_user = await db.users.find_one({"id": other_user_id}, {"_id": 0, "hashed_password": 0})
            
            if other_user and isinstance(other_user.get('created_at'), str):
                other_user['created_at'] = datetime.fromisoformat(other_user['created_at'])
            
            conversations[conv_id] = {
                "conversation_id": conv_id,
                "other_user": other_user,
                "last_message": msg['message'],
                "last_message_time": msg['created_at'],
                "unread_count": 0
            }
        
        # Count unread
        if msg['receiver_id'] == current_user.id and not msg['is_read']:
            conversations[conv_id]['unread_count'] += 1
    
    return list(conversations.values())

# ==================
# Wallet & Withdrawal Routes
# ==================

@api_router.get("/wallet")
async def get_wallet(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers have wallets")
    
    # Get transactions
    transactions = await db.transactions.find({"user_id": current_user.id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    for txn in transactions:
        if isinstance(txn['created_at'], str):
            txn['created_at'] = datetime.fromisoformat(txn['created_at'])
    
    return {
        "balance": current_user.wallet_balance,
        "transactions": transactions
    }

@api_router.post("/withdrawals", response_model=Withdrawal)
async def request_withdrawal(withdrawal: WithdrawalCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers can request withdrawals")
    
    if withdrawal.amount > current_user.wallet_balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    withdrawal_obj = Withdrawal(**withdrawal.model_dump(), provider_id=current_user.id)
    withdrawal_dict = withdrawal_obj.model_dump()
    withdrawal_dict['created_at'] = withdrawal_dict['created_at'].isoformat()
    
    await db.withdrawals.insert_one(withdrawal_dict)
    
    # Deduct from wallet
    await db.users.update_one(
        {"id": current_user.id},
        {"$inc": {"wallet_balance": -withdrawal.amount}}
    )
    
    return withdrawal_obj

@api_router.get("/withdrawals", response_model=List[Withdrawal])
async def get_withdrawals(current_user: User = Depends(get_current_user)):
    query = {}
    if current_user.role == UserRole.PROVIDER:
        query["provider_id"] = current_user.id
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    withdrawals = await db.withdrawals.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    for withdrawal in withdrawals:
        if isinstance(withdrawal['created_at'], str):
            withdrawal['created_at'] = datetime.fromisoformat(withdrawal['created_at'])
        if withdrawal.get('processed_at') and isinstance(withdrawal['processed_at'], str):
            withdrawal['processed_at'] = datetime.fromisoformat(withdrawal['processed_at'])
    
    return withdrawals

# ==================
# Admin Routes
# ==================

@api_router.get("/admin/stats")
async def get_admin_stats(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    total_users = await db.users.count_documents({})
    total_customers = await db.users.count_documents({"role": UserRole.CUSTOMER})
    total_providers = await db.users.count_documents({"role": UserRole.PROVIDER})
    total_services = await db.services.count_documents({})
    total_bookings = await db.bookings.count_documents({})
    total_revenue = await db.transactions.count_documents({"type": TransactionType.COMMISSION})
    
    return {
        "total_users": total_users,
        "total_customers": total_customers,
        "total_providers": total_providers,
        "total_services": total_services,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue
    }

@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    users = await db.users.find({}, {"_id": 0, "hashed_password": 0}).to_list(1000)
    
    for user in users:
        if isinstance(user['created_at'], str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
    
    return users

@api_router.put("/admin/users/{user_id}/status")
async def update_user_status(user_id: str, is_active: bool, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    await db.users.update_one({"id": user_id}, {"$set": {"is_active": is_active}})
    return {"message": "User status updated"}

@api_router.put("/admin/withdrawals/{withdrawal_id}")
async def process_withdrawal(withdrawal_id: str, status: str, admin_notes: Optional[str] = None, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    await db.withdrawals.update_one(
        {"id": withdrawal_id},
        {"$set": {
            "status": status,
            "admin_notes": admin_notes,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Withdrawal processed"}

# Include the router in the main app
app.include_router(api_router)

# Mount Socket.IO
socketio_app = socketio.ASGIApp(sio, other_asgi_app=app)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socketio_app, host="0.0.0.0", port=8001)
