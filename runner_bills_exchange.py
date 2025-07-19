import time
import requests
import os
import psutil

SAVE_FOLDER = "bills_exchange_pdfs"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def generate_bill_input(index):
    return {
        "date": f"2025-07-{(index % 30) + 1:02d}",
        "amount": f"{1000 + index * 5} USD",
        "due_date": f"2025-08-{(index % 30) + 1:02d}",
        "pay_at": f"Pay Location {index}",
        "exporter_bank": f"Exporter Bank {index}",
        "fcy_amount": f"{2000 + index * 7} USD",
        "fcy_words": f"{2000 + index * 7} Dollars only",
        "invoice_number": f"INV-{1000 + index}",
        "invoice_date": f"2025-07-{(index % 30) + 1:02d}",
        "exporter_company": f"Exporter Co. {index}",
        "buyer_name": f"Buyer {index}",
        "buyer_address": f"Address Line {index}, City"
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
                    break  # Exit retry loop

                elif response.status_code == 503:
                    print(f"⏳ Server busy (503). Retrying... ({attempt + 1}/{retries})")
                    time.sleep(3)  # Wait more before retry

                else:
                    print(f"❌ Failed Request #{i} - Status: {response.status_code}")
                    print(f"📝 Response: {response.text}")
                    break  # Don't retry for other errors

            except Exception as e:
                print(f"💥 Error on PDF #{i} (Attempt {attempt + 1}): {e}")
                time.sleep(2)

        time.sleep(2.0)  # Wait to avoid overload

    end = time.time()
    print("\n📊 Performance Report:")
    print(f"⏱️ Time Taken: {round(end - start, 2)} sec")
    print(f"🧠 Memory Used: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
    print(f"⚙️ CPU Usage: {psutil.cpu_percent(interval=1)}%")

if __name__ == "__main__":
    send_bill_requests()
