import webview
import csv
import os
from datetime import datetime

DATA_FILE = "data.csv"
LOG_FILE = "retrieval_log.csv"
VALID_USERS = {"omkar", "akshay", "prajakta", "amar", "shrikant", "sander", "mathijs", "dirk", "rohit", "kedar"}
RESET_USERS = {"omkar", "akshay", "shrikant"}

data = []

def load_data():
    global data
    if not os.path.exists(DATA_FILE):
        data = []
    else:
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                cleaned = {k.strip(): v.strip() for k, v in row.items()}
                data.append(cleaned)
    print("Loaded rows:", len(data))

def save_data():
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Customer ID", "Type", "Offer", "IMSI", "SIM", "MSISDN", "BILL CYCLE", "Used", "User_ID"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print("Saved rows:", len(data))

def log_retrieval(user, cid, type_val, offer_val):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, user, cid, type_val, offer_val])

class Api:
    def verify_user(self, username):
        username = username.strip().lower()
        if username in VALID_USERS:
            return {"status": "success", "user": username, "can_reset": username in RESET_USERS}
        return {"status": "fail"}

    def get_dropdowns(self):
        load_data()
        types = sorted(set(row.get("Type", "").strip() for row in data if row.get("Used", "").strip() == ""))
        offers = sorted(set(row.get("Offer", "").strip() for row in data if row.get("Used", "").strip() == ""))
        cycles = sorted(set(row.get("BILL CYCLE", "").strip() for row in data if row.get("Used", "").strip() == ""))
        print("Dropdowns:", types, offers, cycles)
        return {"types": types, "offers": offers, "cycles": cycles}

    def retrieve_customer(self, user, selected_type, selected_offer, selected_cycle):
        load_data()
        for row in data:
            if (row.get("Type") == selected_type and
                row.get("Offer") == selected_offer and
                row.get("BILL CYCLE") == selected_cycle and
                row.get("Used", "").strip() == ""):
                row["Used"] = "Yes"
                row["User_ID"] = user
                save_data()
                log_retrieval(user, row["Customer ID"], selected_type, selected_offer)
                return {
                    "status": "success",
                    "details": {
                        "Customer ID": row["Customer ID"],
                        "Type": row["Type"],
                        "Offer": row["Offer"],
                        "IMSI": row["IMSI"],
                        "SIM": row["SIM"],
                        "MSISDN": row["MSISDN"],
                        "Bill Cycle": row["BILL CYCLE"]
                    }
                }
        return {"status": "fail"}

    def reset_all(self):
        load_data()
        for row in data:
            row["Used"] = ""
            row["User_ID"] = ""
        save_data()
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        return {"status": "reset"}

if __name__ == "__main__":
    api = Api()
    webview.create_window("VIT Data Retriever", "verify.html", js_api=api, width=1000, height=700)
    webview.start()
