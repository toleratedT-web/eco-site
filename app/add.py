from app import db
from models import Product

solar = Product(
    name="Solar Panel 250W",
    description="High efficiency solar panel for home installation.",
    image_filename="solar.jpg",
    category="solar",
    price=250.00
)

ev_charger = Product(
    name="Fast EV Charger",
    description="Quick charging station for electric vehicles.",
    image_filename="ev.jpg",
    category="ev",
    price=1200.00
)

smart_fridge = Product(
    name="Smart Fridge",
    description="Energy-efficient smart refrigerator for your kitchen.",
    image_filename="appliances.jpg",
    category="appliances",
    price=2548.00
)

db.session.add_all([solar, ev_charger, smart_fridge])
db.session.commit()