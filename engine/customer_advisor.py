# Simulates a telecom store sales conversation
# Shows how a rep recommends plans and accessories

def recommend_plan(usage):
    if usage == "low":
        return "Basic 5GB Plan", 45
    elif usage == "medium":
        return "Standard 20GB Plan", 65
    else:
        return "Unlimited Plan", 90

def recommend_accessories(device):
    if device == "iphone":
        return [("Case", 40), ("Charger", 30)]
    elif device == "android":
        return [("Case", 30), ("Earbuds", 50)]
    else:
        return []

print("=== Customer Needs Assessment ===")
name = input("Customer name: ")
usage = input("Data usage (low/medium/high): ")
device = input("Device type (iphone/android): ")

plan_name, plan_price = recommend_plan(usage)
accessories = recommend_accessories(device)

device_price = 900 if device == "iphone" else 700

print("\n--- Recommendation ---")
print(f"Plan: {plan_name} - ${plan_price}/month")
print(f"Device price: ${device_price}")

total_accessories = 0
for item, price in accessories:
    print(f"Accessory: {item} - ${price}")
    total_accessories += price

total_sale = device_price + total_accessories

print("\n--- Sale Summary ---")
print(f"Customer: {name}")
print(f"Total device + accessories: ${total_sale}")
print(f"Monthly plan: ${plan_price}")
print("Upsell success: accessories added")