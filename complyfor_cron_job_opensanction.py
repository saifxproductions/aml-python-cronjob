import requests
import pymongo
import json
import logging
from datetime import datetime, timezone, timedelta
import time
import os

# --- Logging Setup ---
log_file = "opensanctions_sync.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also print to console
    ]
)


# --- MongoDB Setup ---
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["complyfor_db"]  # Changed to more appropriate name

# === Dataset Configuration ===
DATASETS = [
    "pl_mswia_sanctions",           # 1.3Mb
    "be_fod_sanctions",             # 12mb
    "au_dfat_sanctions",            # 7.9 mb
    "kg_fiu_national",              # 1.8 mb
    "in_mha_banned",                # 233 kb
    "jp_mof_sanctions",             # 8 mb
    "ebrd_ineligible",              # 1.31 mb
    "ca_listed_terrorists",         # 224 kb
    "eu_europol_wanted",            # 28 kb
    "az_fiu_sanctions",             # 35 kb
    "us_occ_enfact",                # 6 mb
    "eu_sanctions_map",             # 1.46 mb
    "ch_seco_sanctions",            # 28 mb
    "gb_hmt_sanctions",             # 14.81 Mb
    "ca_facfoa",                    # 10 KB
    "ru_acf_bribetakers",           # 8 MB
    "ua_nsdc_sanctions",            # 114 MB
    "eu_meps",                      # 1.81 MB
    "iadb_sanctions",               # 1.28 MB
    "adb_sanctions",                # 1.62 MB
    "ru_nsd_isin",                  # 36 MB
    "un_sc_sanctions",              # 2.9 MB
    "md_rise_profiles",             # 1.47 MB
    "us_fbi_most_wanted",           # 585 kb
    "ca_dfatd_sema_sanctions",      # 8.7 mb
    "ae_local_terrorists",          # 380 kb
    "us_cuba_sanctions",            # 759 KB
    "sy_obsalytics_opensyr",        # 22 MB
    "lt_fiu_freezes",               # 58 KB
    "ar_repet",                     # 1.64 MB
    "za_fic_sanctions",             # 2.07 MB
    "ru_fedsfm_wmd",                # 1.5 KB
    "interpol_red_notices",         # 8.3 MB
    "us_ofac_sdn",                  # 66 MB
    "eu_fsf",                       # 13 MB
    "sg_terrorists",                # 33 KB
    "fr_tresor_gels_avoir",         # 20.81 MB
    "nz_russia_sanctions",          # 4.7 MB
    "bg_omnio_poi",                 # 715 KB
    "us_cia_world_leaders",         # 7.5 MB
    "everypolitician",              # 101.31 MB
    "eu_cor_members",               # 887 KB
    "worldbank_debarred",           # 2.27 MB
    "qa_nctc_sanctions",            # 1 MB
    "nl_most_wanted",               # 34.02 KB
    "md_interdictie",               # 48 KB
    "gb_coh_disqualified",          # 19.1 MB
    "us_ofac_cons",                 # 2.94 MB
    "afdb_sanctions",               # 1.11 MB
    "eu_travel_bans",               # 7.87 MB
    "ua_sfms_blacklist",            # 2.08 MB
    "il_mod_terrorists",            # 2.05 MB
]

def get_current_date_string():
    """Get current date in YYYYMMDD format"""
    return datetime.now().strftime("%Y%m%d")

def get_dataset_url(dataset_name, date_string=None):
    """Generate URL with current date"""
    if date_string is None:
        date_string = get_current_date_string()
    
    url = f"https://data.opensanctions.org/datasets/{date_string}/{dataset_name}/targets.nested.json"
    return url

def check_url_exists(url):
    """Check if URL exists without downloading the entire file"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def find_latest_available_date(dataset_name):
    """Find the latest available date for a dataset by checking recent dates"""
    current_date = datetime.now()
    
    # Check last 7 days in case today's data isn't available yet
    for days_back in range(7):
        check_date = current_date - timedelta(days=days_back)
        date_string = check_date.strftime("%Y%m%d")
        url = get_dataset_url(dataset_name, date_string)
        
        if check_url_exists(url):
            logging.info(f"✅ Found data for {dataset_name} on date: {date_string}")
            return date_string, url
    
    # If no recent data found, try the 'latest' endpoint as fallback
    fallback_url = f"https://data.opensanctions.org/datasets/latest/{dataset_name}/targets.nested.json"
    logging.warning(f"⚠️ No recent dated data found for {dataset_name}, using fallback: {fallback_url}")
    return None, fallback_url

# --- Sync Function ---
def fetch_and_store_dataset(dataset_name):
    current_date_string = get_current_date_string()
    
    # Find the latest available data
    data_date, url = find_latest_available_date(dataset_name)
    if data_date:
        logging.info(f"🔄 Downloading {dataset_name} from {url} (data date: {data_date})")
    else:
        logging.info(f"🔄 Downloading {dataset_name} from {url} (using latest endpoint)")

    try:
        # Increase timeout for large datasets
        timeout = 300  # 5 minutes for large files
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        collection = db[dataset_name]
        # Clear existing data for this dataset
        collection.delete_many({})
        
        json_data = []
        line_count = 0
        batch_size = 1000
        
        # Process stream to handle large files efficiently
        for line in response.iter_lines(decode_unicode=True):
            if line and line.strip():
                try:
                    obj = json.loads(line)
                    # Store timezone-aware UTC datetime
                    obj["_fetched_at"] = datetime.now(timezone.utc)
                    obj["_dataset"] = dataset_name  # Add dataset identifier
                    obj["_source_url"] = url  # Track source URL
                    obj["_data_date"] = data_date if data_date else current_date_string  # Track data date
                    json_data.append(obj)
                    line_count += 1
                    
                    # Batch insert to manage memory for large datasets
                    if len(json_data) >= batch_size:
                        collection.insert_many(json_data)
                        logging.info(f"📦 Batch inserted {len(json_data)} records into '{dataset_name}' (total: {line_count})")
                        json_data = []  # Clear batch
                        
                except json.JSONDecodeError as e:
                    logging.warning(f"⚠️ JSON decode error in {dataset_name} at line {line_count}: {str(e)}")
                    continue

        # Insert any remaining records
        if json_data:
            collection.insert_many(json_data)
            logging.info(f"📦 Final batch inserted {len(json_data)} records into '{dataset_name}'")

        # Create index on common fields for better query performance
        try:
            collection.create_index([("_dataset", pymongo.ASCENDING)])
            collection.create_index([("_fetched_at", pymongo.DESCENDING)])
            collection.create_index([("_data_date", pymongo.DESCENDING)])
        except Exception as e:
            logging.warning(f"⚠️ Could not create indexes for {dataset_name}: {e}")

        logging.info(f"✅ Successfully processed {line_count} records for '{dataset_name}' (data date: {data_date})")
        return True, line_count, data_date

    except requests.exceptions.Timeout:
        logging.error(f"⏰ Timeout error processing dataset '{dataset_name}'")
        return False, 0, None
    except requests.exceptions.HTTPError as e:
        logging.error(f"🌐 HTTP error {e.response.status_code} for dataset '{dataset_name}': {e}")
        return False, 0, None
    except requests.exceptions.RequestException as e:
        logging.error(f"🌐 Network error processing dataset '{dataset_name}': {str(e)}")
        return False, 0, None
    except Exception as e:
        logging.error(f"❌ Error processing dataset '{dataset_name}': {str(e)}")
        return False, 0, None

# --- Progress Tracking ---
def main():
    current_date = get_current_date_string()
    total_datasets = len(DATASETS)
    logging.info(f"🚀 Starting OpenSanctions sync job for {total_datasets} datasets on date {current_date}")
    
    completed = 0
    failed = []
    total_records = 0
    
    for dataset in DATASETS:
        try:
            start_time = time.time()
            success, record_count, data_date = fetch_and_store_dataset(dataset)
            end_time = time.time()
            duration = end_time - start_time
            
            if success:
                completed += 1
                total_records += record_count
            else:
                failed.append(dataset)
                
            progress = (completed / total_datasets) * 100
            status = "✅" if success else "❌"
            logging.info(f"📊 {status} Progress: {completed}/{total_datasets} ({progress:.1f}%) - {dataset}: {record_count} records in {duration:.2f}s")
            
            # Small delay to be respectful to the server
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"💥 Critical error processing {dataset}: {str(e)}")
            failed.append(dataset)
    
    # Summary
    logging.info(f"\n📈 SYNC SUMMARY for {current_date}")
    logging.info(f"✅ Successfully processed: {completed}/{total_datasets} datasets")
    logging.info(f"📊 Total records imported: {total_records:,}")
    if failed:
        logging.warning(f"❌ Failed datasets: {failed}")
    else:
        logging.info("🎉 All datasets processed successfully!")
    
    # Save sync metadata
    sync_metadata = {
        "sync_date": datetime.now(timezone.utc),
        "data_date": current_date,
        "total_datasets": total_datasets,
        "successful_datasets": completed,
        "failed_datasets": failed,
        "total_records": total_records,
        "duration_seconds": time.time() - start_time
    }
    
    db["sync_metadata"].insert_one(sync_metadata)
    logging.info("💾 Sync metadata saved to database")
    logging.info("OpenSanctions sync job finished.\n")

# --- Function to run as a daily cron job ---
def daily_sync():
    """Main function to run as a daily cron job"""
    logging.info("=" * 60)
    logging.info("🕒 DAILY OPEN SANCTIONS SYNC STARTED")
    logging.info("=" * 60)
    
    main()
    
    logging.info("=" * 60)
    logging.info("🕒 DAILY OPEN SANCTIONS SYNC COMPLETED")
    logging.info("=" * 60)

if __name__ == "__main__":
    daily_sync()