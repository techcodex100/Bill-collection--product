import time
import requests
import os
import psutil
from faker import Faker

fake = Faker()
SAVE_FOLDER = "bills_exchange_pdfs"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def generate_bill_input(index):
    amount = fake.random_int(min=1000, max=5000)
    due_date = fake.date_between(start_date="+15d", end_date="+60d")
    invoice_date = fake.date_between(start_date="-30d", end_date="today")

    return {
        "date": fake.date(),
        "amount": f"{amount} USD",
        "due_date": due_date.strftime("%Y-%m-%d"),
        "pay_at": fake.city(),
        "exporter_bank": fake.company(),
        "fcy_amount": f"{amount + 1000} USD",
        "fcy_words": f"{amount + 1000} Dollars only",
        "invoice_number": f"INV-{fake.random_int(min=10000, max=99999)}",
        "invoice_date": invoice_date.strftime("%Y-%m-%d"),
        "exporter_company": fake.company(),
        "buyer_name": fake.name(),
        "buyer_address": fake.address().replace("\n", ", ")
    }

def send_bill_requests():
    print("🚀 Auto Bill PDF Generation Started...\n")
    start = time.time()
    total_pdfs = 50

    for i in range(1, total_pdfs + 1):
        print(f"\n📤 Generating Bill PDF #{i}...")
        data = generate_bill_input(i)

        retries = 3
        for attempt in range(retries):
            try:
                response = requests.post(
                    "https://bill-collection-product.onrender.com/generate-pdf/",
                    json=data
                )

                if response.status_code == 200 and response.headers.get("content-type") == "application/pdf":
                    file_path = os.path.join(SAVE_FOLDER, f"bill_exchange_{i}.pdf")
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ PDF #{i} saved at: {file_path}")
                    break  # Success

                elif response.status_code == 503:
                    print(f"⏳ Server busy (503). Retrying... ({attempt + 1}/{retries})")
                    time.sleep(3)

                else:
                    print(f"❌ Failed Request #{i} - Status: {response.status_code}")
                    print(f"📝 Response: {response.text}")
                    break

            except Exception as e:
                print(f"💥 Error on PDF #{i} (Attempt {attempt + 1}): {e}")
                time.sleep(2)

        time.sleep(2.0)  # Avoid server overload

    end = time.time()
    print("\n📊 Performance Report:")
    print(f"⏱️ Time Taken: {round(end - start, 2)} sec")
    print(f"🧠 Memory Used: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
    print(f"⚙️ CPU Usage: {psutil.cpu_percent(interval=1)}%")

if __name__ == "__main__":
    send_bill_requests()
