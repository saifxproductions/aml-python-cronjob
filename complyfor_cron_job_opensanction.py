# # import requests
# # import pymongo
# # import json
# # import logging
# # from datetime import datetime, timezone, timedelta
# # import time
# # import os

# # # --- Logging Setup ---
# # log_file = "opensanctions_sync.log"
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s [%(levelname)s] %(message)s",
# #     handlers=[
# #         logging.FileHandler(log_file),
# #         logging.StreamHandler()  # Also print to console
# #     ]
# # )


# # # --- MongoDB Setup ---
# # client = pymongo.MongoClient("mongodb://localhost:27017/")
# # db = client["complyfor_db"]  # Changed to more appropriate name

# # # === Dataset Configuration ===
# # DATASETS = [
# #     "pl_mswia_sanctions",           # 1.3Mb
# #     "be_fod_sanctions",             # 12mb
# #     "au_dfat_sanctions",            # 7.9 mb
# #     "kg_fiu_national",              # 1.8 mb
# #     "in_mha_banned",                # 233 kb
# #     "jp_mof_sanctions",             # 8 mb
# #     "ebrd_ineligible",              # 1.31 mb
# #     "ca_listed_terrorists",         # 224 kb
# #     "eu_europol_wanted",            # 28 kb
# #     "az_fiu_sanctions",             # 35 kb
# #     "us_occ_enfact",                # 6 mb
# #     "eu_sanctions_map",             # 1.46 mb
# #     "ch_seco_sanctions",            # 28 mb
# #     "gb_hmt_sanctions",             # 14.81 Mb
# #     "ca_facfoa",                    # 10 KB
# #     "ru_acf_bribetakers",           # 8 MB
# #     "ua_nsdc_sanctions",            # 114 MB
# #     "eu_meps",                      # 1.81 MB
# #     "iadb_sanctions",               # 1.28 MB
# #     "adb_sanctions",                # 1.62 MB
# #     "ru_nsd_isin",                  # 36 MB
# #     "un_sc_sanctions",              # 2.9 MB
# #     "md_rise_profiles",             # 1.47 MB
# #     "us_fbi_most_wanted",           # 585 kb
# #     "ca_dfatd_sema_sanctions",      # 8.7 mb
# #     "ae_local_terrorists",          # 380 kb
# #     "us_cuba_sanctions",            # 759 KB
# #     "sy_obsalytics_opensyr",        # 22 MB
# #     "lt_fiu_freezes",               # 58 KB
# #     "ar_repet",                     # 1.64 MB
# #     "za_fic_sanctions",             # 2.07 MB
# #     "ru_fedsfm_wmd",                # 1.5 KB
# #     "interpol_red_notices",         # 8.3 MB
# #     "us_ofac_sdn",                  # 66 MB
# #     "eu_fsf",                       # 13 MB
# #     "sg_terrorists",                # 33 KB
# #     "fr_tresor_gels_avoir",         # 20.81 MB
# #     "nz_russia_sanctions",          # 4.7 MB
# #     "bg_omnio_poi",                 # 715 KB
# #     "us_cia_world_leaders",         # 7.5 MB
# #     "everypolitician",              # 101.31 MB
# #     "eu_cor_members",               # 887 KB
# #     "worldbank_debarred",           # 2.27 MB
# #     "qa_nctc_sanctions",            # 1 MB
# #     "nl_most_wanted",               # 34.02 KB
# #     "md_interdictie",               # 48 KB
# #     "gb_coh_disqualified",          # 19.1 MB
# #     "us_ofac_cons",                 # 2.94 MB
# #     "afdb_sanctions",               # 1.11 MB
# #     "eu_travel_bans",               # 7.87 MB
# #     "ua_sfms_blacklist",            # 2.08 MB
# #     "il_mod_terrorists",            # 2.05 MB
# # ]

# # def get_current_date_string():
# #     """Get current date in YYYYMMDD format"""
# #     return datetime.now().strftime("%Y%m%d")

# # def get_dataset_url(dataset_name, date_string=None):
# #     """Generate URL with current date"""
# #     if date_string is None:
# #         date_string = get_current_date_string()
    
# #     url = f"https://data.opensanctions.org/datasets/{date_string}/{dataset_name}/targets.nested.json"
# #     return url

# # def check_url_exists(url):
# #     """Check if URL exists without downloading the entire file"""
# #     try:
# #         response = requests.head(url, timeout=10)
# #         return response.status_code == 200
# #     except requests.RequestException:
# #         return False

# # def find_latest_available_date(dataset_name):
# #     """Find the latest available date for a dataset by checking recent dates"""
# #     current_date = datetime.now()
    
# #     # Check last 7 days in case today's data isn't available yet
# #     for days_back in range(7):
# #         check_date = current_date - timedelta(days=days_back)
# #         date_string = check_date.strftime("%Y%m%d")
# #         url = get_dataset_url(dataset_name, date_string)
        
# #         if check_url_exists(url):
# #             logging.info(f"✅ Found data for {dataset_name} on date: {date_string}")
# #             return date_string, url
    
# #     # If no recent data found, try the 'latest' endpoint as fallback
# #     fallback_url = f"https://data.opensanctions.org/datasets/latest/{dataset_name}/targets.nested.json"
# #     logging.warning(f"⚠️ No recent dated data found for {dataset_name}, using fallback: {fallback_url}")
# #     return None, fallback_url

# # # --- Sync Function ---
# # def fetch_and_store_dataset(dataset_name):
# #     current_date_string = get_current_date_string()
    
# #     # Find the latest available data
# #     data_date, url = find_latest_available_date(dataset_name)
# #     if data_date:
# #         logging.info(f"🔄 Downloading {dataset_name} from {url} (data date: {data_date})")
# #     else:
# #         logging.info(f"🔄 Downloading {dataset_name} from {url} (using latest endpoint)")

# #     try:
# #         # Increase timeout for large datasets
# #         timeout = 300  # 5 minutes for large files
# #         response = requests.get(url, timeout=timeout, stream=True)
# #         response.raise_for_status()
        
# #         collection = db[dataset_name]
# #         # Clear existing data for this dataset
# #         collection.delete_many({})
        
# #         json_data = []
# #         line_count = 0
# #         batch_size = 1000
        
# #         # Process stream to handle large files efficiently
# #         for line in response.iter_lines(decode_unicode=True):
# #             if line and line.strip():
# #                 try:
# #                     obj = json.loads(line)
# #                     # Store timezone-aware UTC datetime
# #                     obj["_fetched_at"] = datetime.now(timezone.utc)
# #                     obj["_dataset"] = dataset_name  # Add dataset identifier
# #                     obj["_source_url"] = url  # Track source URL
# #                     obj["_data_date"] = data_date if data_date else current_date_string  # Track data date
# #                     json_data.append(obj)
# #                     line_count += 1
                    
# #                     # Batch insert to manage memory for large datasets
# #                     if len(json_data) >= batch_size:
# #                         collection.insert_many(json_data)
# #                         logging.info(f"📦 Batch inserted {len(json_data)} records into '{dataset_name}' (total: {line_count})")
# #                         json_data = []  # Clear batch
                        
# #                 except json.JSONDecodeError as e:
# #                     logging.warning(f"⚠️ JSON decode error in {dataset_name} at line {line_count}: {str(e)}")
# #                     continue

# #         # Insert any remaining records
# #         if json_data:
# #             collection.insert_many(json_data)
# #             logging.info(f"📦 Final batch inserted {len(json_data)} records into '{dataset_name}'")

# #         # Create index on common fields for better query performance
# #         try:
# #             collection.create_index([("_dataset", pymongo.ASCENDING)])
# #             collection.create_index([("_fetched_at", pymongo.DESCENDING)])
# #             collection.create_index([("_data_date", pymongo.DESCENDING)])
# #         except Exception as e:
# #             logging.warning(f"⚠️ Could not create indexes for {dataset_name}: {e}")

# #         logging.info(f"✅ Successfully processed {line_count} records for '{dataset_name}' (data date: {data_date})")
# #         return True, line_count, data_date

# #     except requests.exceptions.Timeout:
# #         logging.error(f"⏰ Timeout error processing dataset '{dataset_name}'")
# #         return False, 0, None
# #     except requests.exceptions.HTTPError as e:
# #         logging.error(f"🌐 HTTP error {e.response.status_code} for dataset '{dataset_name}': {e}")
# #         return False, 0, None
# #     except requests.exceptions.RequestException as e:
# #         logging.error(f"🌐 Network error processing dataset '{dataset_name}': {str(e)}")
# #         return False, 0, None
# #     except Exception as e:
# #         logging.error(f"❌ Error processing dataset '{dataset_name}': {str(e)}")
# #         return False, 0, None

# # # --- Progress Tracking ---
# # def main():
# #     current_date = get_current_date_string()
# #     total_datasets = len(DATASETS)
# #     logging.info(f"🚀 Starting OpenSanctions sync job for {total_datasets} datasets on date {current_date}")
    
# #     completed = 0
# #     failed = []
# #     total_records = 0
    
# #     for dataset in DATASETS:
# #         try:
# #             start_time = time.time()
# #             success, record_count, data_date = fetch_and_store_dataset(dataset)
# #             end_time = time.time()
# #             duration = end_time - start_time
            
# #             if success:
# #                 completed += 1
# #                 total_records += record_count
# #             else:
# #                 failed.append(dataset)
                
# #             progress = (completed / total_datasets) * 100
# #             status = "✅" if success else "❌"
# #             logging.info(f"📊 {status} Progress: {completed}/{total_datasets} ({progress:.1f}%) - {dataset}: {record_count} records in {duration:.2f}s")
            
# #             # Small delay to be respectful to the server
# #             time.sleep(2)
            
# #         except Exception as e:
# #             logging.error(f"💥 Critical error processing {dataset}: {str(e)}")
# #             failed.append(dataset)
    
# #     # Summary
# #     logging.info(f"\n📈 SYNC SUMMARY for {current_date}")
# #     logging.info(f"✅ Successfully processed: {completed}/{total_datasets} datasets")
# #     logging.info(f"📊 Total records imported: {total_records:,}")
# #     if failed:
# #         logging.warning(f"❌ Failed datasets: {failed}")
# #     else:
# #         logging.info("🎉 All datasets processed successfully!")
    
# #     # Save sync metadata
# #     sync_metadata = {
# #         "sync_date": datetime.now(timezone.utc),
# #         "data_date": current_date,
# #         "total_datasets": total_datasets,
# #         "successful_datasets": completed,
# #         "failed_datasets": failed,
# #         "total_records": total_records,
# #         "duration_seconds": time.time() - start_time
# #     }
    
# #     db["sync_metadata"].insert_one(sync_metadata)
# #     logging.info("💾 Sync metadata saved to database")
# #     logging.info("OpenSanctions sync job finished.\n")

# # # --- Function to run as a daily cron job ---
# # def daily_sync():
# #     """Main function to run as a daily cron job"""
# #     logging.info("=" * 60)
# #     logging.info("🕒 DAILY OPEN SANCTIONS SYNC STARTED")
# #     logging.info("=" * 60)
    
# #     main()
    
# #     logging.info("=" * 60)
# #     logging.info("🕒 DAILY OPEN SANCTIONS SYNC COMPLETED")
# #     logging.info("=" * 60)

# # if __name__ == "__main__":
# #     daily_sync()

# import requests
# import pymongo
# import json
# import logging
# from datetime import datetime, timezone, timedelta
# import time
# import os
# from typing import Dict, List, Optional
# import argparse
# import re

# # --- Logging Setup ---
# log_file = "opensanctions_sync.log"
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         logging.FileHandler(log_file),
#         logging.StreamHandler()  # Also print to console
#     ]
# )

# # --- MongoDB Setup ---
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["complyfor_db"]

# # === Dataset Configuration ===
# DATASETS = [
#     "pl_mswia_sanctions",           # 1.3Mb
#     "be_fod_sanctions",             # 12mb
#     "au_dfat_sanctions",            # 7.9 mb
#     "kg_fiu_national",              # 1.8 mb
#     "in_mha_banned",                # 233 kb
#     "jp_mof_sanctions",             # 8 mb
#     "ebrd_ineligible",              # 1.31 mb
#     "ca_listed_terrorists",         # 224 kb
#     "eu_europol_wanted",            # 28 kb
#     "az_fiu_sanctions",             # 35 kb
#     "us_occ_enfact",                # 6 mb
#     "eu_sanctions_map",             # 1.46 mb
#     "ch_seco_sanctions",            # 28 mb
#     "gb_hmt_sanctions",             # 14.81 Mb
#     "ca_facfoa",                    # 10 KB
#     "ru_acf_bribetakers",           # 8 MB
#     "ua_nsdc_sanctions",            # 114 MB
#     "eu_meps",                      # 1.81 MB
#     "iadb_sanctions",               # 1.28 MB
#     "adb_sanctions",                # 1.62 MB
#     "ru_nsd_isin",                  # 36 MB
#     "un_sc_sanctions",              # 2.9 MB
#     "md_rise_profiles",             # 1.47 MB
#     "us_fbi_most_wanted",           # 585 kb
#     "ca_dfatd_sema_sanctions",      # 8.7 mb
#     "ae_local_terrorists",          # 380 kb
#     "us_cuba_sanctions",            # 759 KB
#     "sy_obsalytics_opensyr",        # 22 MB
#     "lt_fiu_freezes",               # 58 KB
#     "ar_repet",                     # 1.64 MB
#     "za_fic_sanctions",             # 2.07 MB
#     "ru_fedsfm_wmd",                # 1.5 KB
#     "interpol_red_notices",         # 8.3 MB
#     "us_ofac_sdn",                  # 66 MB
#     "eu_fsf",                       # 13 MB
#     "sg_terrorists",                # 33 KB
#     "fr_tresor_gels_avoir",         # 20.81 MB
#     "nz_russia_sanctions",          # 4.7 MB
#     "bg_omnio_poi",                 # 715 KB
#     "us_cia_world_leaders",         # 7.5 MB
#     "everypolitician",              # 101.31 MB
#     "eu_cor_members",               # 887 KB
#     "worldbank_debarred",           # 2.27 MB
#     "qa_nctc_sanctions",            # 1 MB
#     "nl_most_wanted",               # 34.02 KB
#     "md_interdictie",               # 48 KB
#     "gb_coh_disqualified",          # 19.1 MB
#     "us_ofac_cons",                 # 2.94 MB
#     "afdb_sanctions",               # 1.11 MB
#     "eu_travel_bans",               # 7.87 MB
#     "ua_sfms_blacklist",            # 2.08 MB
#     "il_mod_terrorists",            # 2.05 MB
# ]

# class ScrapingLogger:
#     """Manages scraping operation logs in MongoDB - Hybrid Approach"""
    
#     def __init__(self, db):
#         self.db = db
#         self.operations_collection = db["scraping_operations"]
#         self.daily_summary_collection = db["scraping_daily_summary"]
#         self._ensure_indexes()
#         logging.info("✅ ScrapingLogger initialized")
    
#     def _ensure_indexes(self):
#         """Create optimized indexes for both collections"""
#         try:
#             # Indexes for individual operations
#             self.operations_collection.create_index([("date", pymongo.DESCENDING)])
#             self.operations_collection.create_index([("dataset_name", pymongo.ASCENDING)])
#             self.operations_collection.create_index([("status", pymongo.ASCENDING)])
#             self.operations_collection.create_index([("operation_id", pymongo.ASCENDING)], unique=True)
#             self.operations_collection.create_index([("data_date", pymongo.DESCENDING)])
            
#             # Indexes for daily summaries
#             self.daily_summary_collection.create_index([("date", pymongo.DESCENDING)], unique=True)
            
#             logging.debug("✅ Created optimized indexes for logging collections")
#         except Exception as e:
#             logging.error(f"❌ Error creating indexes: {e}")
    
#     def log_operation_start(self, dataset_name: str, collection_name: str, 
#                            source_url: str = None, data_date: str = None) -> str:
#         """Log the start of a scraping operation and return operation ID"""
#         try:
#             operation_id = f"{dataset_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
#             # Extract data_date from URL if not provided
#             if not data_date and source_url:
#                 match = re.search(r'datasets/(\d{8})/', source_url)
#                 if match:
#                     data_date = match.group(1)
            
#             operation_log = {
#                 "operation_id": operation_id,
#                 "dataset_name": dataset_name,
#                 "collection_name": collection_name,
#                 "date": datetime.now(timezone.utc).strftime("%Y%m%d"),
#                 "start_time": datetime.now(timezone.utc),
#                 "status": "in_progress",
#                 "records_processed": 0,
#                 "records_inserted": 0,
#                 "records_deleted": 0,
#                 "source_url": source_url,
#                 "data_date": data_date,  # Store data_date from the beginning
#                 "metadata": {
#                     "host": os.uname().nodename if hasattr(os, 'uname') else "unknown",
#                     "python_version": os.sys.version,
#                     "script_version": "1.0.0"
#                 }
#             }
            
#             result = self.operations_collection.insert_one(operation_log)
#             logging.debug(f"📝 Started operation: {operation_id} (data_date: {data_date})")
#             return operation_id
#         except Exception as e:
#             logging.error(f"❌ Error logging operation start: {e}")
#             return f"error_{int(time.time())}"
    
#     def log_operation_success(self, operation_id: str, records_processed: int, 
#                             records_inserted: int, records_deleted: int = 0,
#                             data_date: str = None, **kwargs):
#         """Log successful completion of a scraping operation"""
#         try:
#             operation = self.operations_collection.find_one({"operation_id": operation_id})
#             if not operation:
#                 logging.error(f"⚠️ Operation {operation_id} not found in database")
#                 return
            
#             start_time = operation.get("start_time")
#             if isinstance(start_time, str):
#                 start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
#             duration = (datetime.now(timezone.utc) - start_time).total_seconds() if start_time else 0
            
#             # Use data_date from parameters or keep existing one
#             final_data_date = data_date if data_date else operation.get("data_date")
            
#             update_data = {
#                 "end_time": datetime.now(timezone.utc),
#                 "status": "success",
#                 "records_processed": records_processed,
#                 "records_inserted": records_inserted,
#                 "records_deleted": records_deleted,
#                 "duration_seconds": round(duration, 2),
#                 "data_date": final_data_date  # Ensure data_date is saved
#             }
            
#             # Update metadata
#             current_metadata = operation.get("metadata", {})
#             current_metadata.update(kwargs)
#             update_data["metadata"] = current_metadata
            
#             result = self.operations_collection.update_one(
#                 {"operation_id": operation_id},
#                 {"$set": update_data}
#             )
            
#             if result.modified_count > 0:
#                 logging.info(f"✅ Completed operation: {operation_id} ({records_processed} records, data_date: {final_data_date})")
#             else:
#                 logging.warning(f"⚠️ No document updated for operation: {operation_id}")
                
#         except Exception as e:
#             logging.error(f"❌ Error logging operation success for {operation_id}: {e}")
    
#     def log_operation_failure(self, operation_id: str, error_message: str, **kwargs):
#         """Log failed scraping operation"""
#         try:
#             operation = self.operations_collection.find_one({"operation_id": operation_id})
#             if not operation:
#                 logging.error(f"⚠️ Operation {operation_id} not found in database")
#                 return
            
#             start_time = operation.get("start_time")
#             if isinstance(start_time, str):
#                 start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
#             duration = (datetime.now(timezone.utc) - start_time).total_seconds() if start_time else 0
            
#             update_data = {
#                 "end_time": datetime.now(timezone.utc),
#                 "status": "failed",
#                 "error_message": error_message[:500],  # Limit error message length
#                 "duration_seconds": round(duration, 2)
#             }
            
#             # Update metadata
#             current_metadata = operation.get("metadata", {})
#             current_metadata.update(kwargs)
#             update_data["metadata"] = current_metadata
            
#             result = self.operations_collection.update_one(
#                 {"operation_id": operation_id},
#                 {"$set": update_data}
#             )
            
#             if result.modified_count > 0:
#                 logging.info(f"❌ Marked operation as failed: {operation_id} (duration: {duration:.2f}s)")
#             else:
#                 logging.warning(f"⚠️ No document updated for failed operation: {operation_id}")
                
#         except Exception as e:
#             logging.error(f"❌ Error logging operation failure for {operation_id}: {e}")
    
#     def create_daily_summary(self, date_str: str = None) -> Dict:
#         """Create or update daily summary from all operations of that day"""
#         if date_str is None:
#             date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        
#         try:
#             # Aggregate all operations for this date
#             pipeline = [
#                 {"$match": {"date": date_str}},
#                 {"$group": {
#                     "_id": "$date",
#                     "total_operations": {"$sum": 1},
#                     "successful_operations": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
#                     "failed_operations": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
#                     "in_progress_operations": {"$sum": {"$cond": [{"$eq": ["$status", "in_progress"]}, 1, 0]}},
#                     "total_records_processed": {"$sum": "$records_processed"},
#                     "total_records_inserted": {"$sum": "$records_inserted"},
#                     "total_records_deleted": {"$sum": "$records_deleted"},
#                     "avg_duration_seconds": {"$avg": "$duration_seconds"},
#                     "max_duration_seconds": {"$max": "$duration_seconds"},
#                     "min_duration_seconds": {"$min": "$duration_seconds"},
#                     "operations": {"$push": {
#                         "operation_id": "$operation_id",
#                         "dataset_name": "$dataset_name",
#                         "status": "$status",
#                         "data_date": "$data_date",
#                         "records_processed": "$records_processed",
#                         "duration_seconds": "$duration_seconds",
#                         "error_message": "$error_message"
#                     }},
#                     "data_dates_used": {"$addToSet": "$data_date"},
#                     "failed_datasets": {
#                         "$push": {
#                             "$cond": [
#                                 {"$eq": ["$status", "failed"]},
#                                 {"name": "$dataset_name", "error": "$error_message"},
#                                 None
#                             ]
#                         }
#                     },
#                     "first_operation": {"$min": "$start_time"},
#                     "last_operation": {"$max": "$end_time"}
#                 }},
#                 {"$project": {
#                     "date": "$_id",
#                     "total_operations": 1,
#                     "successful_operations": 1,
#                     "failed_operations": 1,
#                     "in_progress_operations": 1,
#                     "total_records_processed": 1,
#                     "total_records_inserted": 1,
#                     "total_records_deleted": 1,
#                     "success_rate": {
#                         "$cond": [
#                             {"$gt": ["$total_operations", 0]},
#                             {"$round": [
#                                 {"$multiply": [
#                                     {"$divide": ["$successful_operations", "$total_operations"]},
#                                     100
#                                 ]},
#                                 2
#                             ]},
#                             0
#                         ]
#                     },
#                     "avg_duration_seconds": {"$ifNull": [{"$round": ["$avg_duration_seconds", 2]}, 0]},
#                     "max_duration_seconds": {"$ifNull": [{"$round": ["$max_duration_seconds", 2]}, 0]},
#                     "min_duration_seconds": {"$ifNull": [{"$round": ["$min_duration_seconds", 2]}, 0]},
#                     "total_duration_hours": {
#                         "$cond": [
#                             {"$and": [{"$ne": ["$first_operation", None]}, {"$ne": ["$last_operation", None]}]},
#                             {"$round": [{
#                                 "$divide": [{
#                                     "$subtract": ["$last_operation", "$first_operation"]
#                                 }, 3600000]  # Convert ms to hours
#                             }, 2]},
#                             0
#                         ]
#                     },
#                     "operations": {"$slice": ["$operations", 100]},
#                     "data_dates_used": {
#                         "$filter": {
#                             "input": "$data_dates_used",
#                             "as": "date",
#                             "cond": {"$ne": ["$$date", None]}
#                         }
#                     },
#                     "failed_datasets": {
#                         "$filter": {
#                             "input": "$failed_datasets",
#                             "as": "failed",
#                             "cond": {"$ne": ["$$failed", None]}
#                         }
#                     },
#                     "generated_at": datetime.now(timezone.utc)
#                 }}
#             ]
            
#             result = list(self.operations_collection.aggregate(pipeline))
            
#             if result:
#                 summary = result[0]
#                 # Clean up the operations list
#                 if "operations" in summary:
#                     for op in summary["operations"]:
#                         if op.get("error_message") is None:
#                             op.pop("error_message", None)
                
#                 # Upsert daily summary
#                 self.daily_summary_collection.update_one(
#                     {"date": date_str},
#                     {"$set": summary},
#                     upsert=True
#                 )
                
#                 logging.info(f"📊 Created daily summary for {date_str}: "
#                            f"{summary['successful_operations']}/{summary['total_operations']} successful")
#                 return summary
            
#             logging.warning(f"⚠️ No operations found for date {date_str}")
#             return None
            
#         except Exception as e:
#             logging.error(f"❌ Error creating daily summary: {e}")
#             return None
    
#     def get_daily_summary(self, date_str: str) -> Optional[Dict]:
#         """Get daily summary by date"""
#         return self.daily_summary_collection.find_one({"date": date_str})
    
#     def get_operation_history(self, dataset_name: Optional[str] = None, 
#                              days_back: int = 7, limit: int = 50) -> List[Dict]:
#         """Get operation history with optional filters"""
#         query = {}
        
#         # Date filter
#         cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
#         query["date"] = {"$gte": cutoff_date}
        
#         # Dataset filter
#         if dataset_name:
#             query["dataset_name"] = dataset_name
        
#         return list(self.operations_collection.find(query)
#                    .sort("start_time", pymongo.DESCENDING)
#                    .limit(limit))
    
#     def get_dataset_statistics(self, dataset_name: str, days_back: int = 30) -> Dict:
#         """Get statistics for a specific dataset"""
#         cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
        
#         try:
#             pipeline = [
#                 {"$match": {
#                     "dataset_name": dataset_name,
#                     "date": {"$gte": cutoff_date},
#                     "status": {"$in": ["success", "failed"]}
#                 }},
#                 {"$group": {
#                     "_id": "$dataset_name",
#                     "total_operations": {"$sum": 1},
#                     "successful_operations": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
#                     "failed_operations": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
#                     "total_records_processed": {"$sum": "$records_processed"},
#                     "total_records_inserted": {"$sum": "$records_inserted"},
#                     "latest_data_date": {"$max": "$data_date"},
#                     "last_scraped": {"$max": "$end_time"},
#                     "avg_duration_seconds": {"$avg": "$duration_seconds"},
#                     "success_rate": {
#                         "$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
#                     }
#                 }},
#                 {"$project": {
#                     "dataset_name": "$_id",
#                     "total_operations": 1,
#                     "successful_operations": 1,
#                     "failed_operations": 1,
#                     "total_records_processed": 1,
#                     "total_records_inserted": 1,
#                     "latest_data_date": 1,
#                     "last_scraped": 1,
#                     "avg_duration_seconds": {"$ifNull": [{"$round": ["$avg_duration_seconds", 2]}, 0]},
#                     "success_rate": {"$ifNull": [{"$round": [{"$multiply": ["$success_rate", 100]}, 2]}, 0]}
#                 }}
#             ]
            
#             result = list(self.operations_collection.aggregate(pipeline))
#             return result[0] if result else {}
#         except Exception as e:
#             logging.error(f"❌ Error getting dataset statistics: {e}")
#             return {}
    
#     def cleanup_old_logs(self, days_to_keep: int = 90):
#         """Clean up logs older than specified days"""
#         try:
#             cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).strftime("%Y%m%d")
            
#             # Delete old operations
#             ops_result = self.operations_collection.delete_many({"date": {"$lt": cutoff_date}})
            
#             # Delete old summaries
#             summary_result = self.daily_summary_collection.delete_many({"date": {"$lt": cutoff_date}})
            
#             logging.info(f"🧹 Cleaned up {ops_result.deleted_count} old operations and "
#                         f"{summary_result.deleted_count} old summaries (older than {days_to_keep} days)")
#             return ops_result.deleted_count + summary_result.deleted_count
#         except Exception as e:
#             logging.error(f"❌ Error cleaning up old logs: {e}")
#             return 0
    
#     def fix_missing_data_dates(self):
#         """Fix operations missing data_date by extracting from source_url"""
#         try:
#             operations = self.operations_collection.find({
#                 "data_date": {"$exists": False},
#                 "source_url": {"$exists": True, "$ne": None}
#             })
            
#             fixed_count = 0
#             for op in operations:
#                 url = op.get("source_url", "")
#                 match = re.search(r'datasets/(\d{8})/', url)
#                 if match:
#                     data_date = match.group(1)
#                     self.operations_collection.update_one(
#                         {"_id": op["_id"]},
#                         {"$set": {"data_date": data_date}}
#                     )
#                     fixed_count += 1
#                     logging.debug(f"Fixed data_date for {op['operation_id']}: {data_date}")
            
#             if fixed_count > 0:
#                 logging.info(f"🔧 Fixed {fixed_count} operations missing data_date")
            
#             return fixed_count
#         except Exception as e:
#             logging.error(f"❌ Error fixing missing data_dates: {e}")
#             return 0

# # Initialize the scraping logger globally
# scraping_logger = ScrapingLogger(db)

# def get_current_date_string():
#     """Get current date in YYYYMMDD format"""
#     return datetime.now().strftime("%Y%m%d")

# def get_dataset_url(dataset_name, date_string=None):
#     """Generate URL with current date"""
#     if date_string is None:
#         date_string = get_current_date_string()
    
#     url = f"https://data.opensanctions.org/datasets/{date_string}/{dataset_name}/targets.nested.json"
#     return url

# def check_url_exists(url):
#     """Check if URL exists without downloading the entire file"""
#     try:
#         response = requests.head(url, timeout=10)
#         return response.status_code == 200
#     except requests.RequestException:
#         return False

# def find_latest_available_date(dataset_name):
#     """Find the latest available date for a dataset by checking recent dates"""
#     current_date = datetime.now()
    
#     # Check last 7 days in case today's data isn't available yet
#     for days_back in range(7):
#         check_date = current_date - timedelta(days=days_back)
#         date_string = check_date.strftime("%Y%m%d")
#         url = get_dataset_url(dataset_name, date_string)
        
#         if check_url_exists(url):
#             logging.info(f"✅ Found data for {dataset_name} on date: {date_string}")
#             return date_string, url
    
#     # If no recent data found, try the 'latest' endpoint as fallback
#     fallback_url = f"https://data.opensanctions.org/datasets/latest/{dataset_name}/targets.nested.json"
#     logging.warning(f"⚠️ No recent dated data found for {dataset_name}, using fallback: {fallback_url}")
#     return None, fallback_url

# def fetch_and_store_dataset(dataset_name):
#     """Fetch and store dataset with comprehensive logging"""
#     current_date_string = get_current_date_string()
    
#     # Find the latest available data
#     data_date, url = find_latest_available_date(dataset_name)
#     if data_date:
#         logging.info(f"🔄 Downloading {dataset_name} from {url} (data date: {data_date})")
#     else:
#         logging.info(f"🔄 Downloading {dataset_name} from {url} (using latest endpoint)")
    
#     # Log operation start - PASS data_date to the logger
#     operation_id = scraping_logger.log_operation_start(
#         dataset_name=dataset_name,
#         collection_name=dataset_name,
#         source_url=url,
#         data_date=data_date  # Pass data_date here
#     )
    
#     try:
#         # Increase timeout for large datasets
#         timeout = 300
#         response = requests.get(url, timeout=timeout, stream=True)
#         response.raise_for_status()
        
#         collection = db[dataset_name]
#         # Clear existing data for this dataset
#         delete_result = collection.delete_many({})
#         records_deleted = delete_result.deleted_count
        
#         json_data = []
#         line_count = 0
#         batch_size = 1000
        
#         # Process stream to handle large files efficiently
#         for line in response.iter_lines(decode_unicode=True):
#             if line and line.strip():
#                 try:
#                     obj = json.loads(line)
#                     # Store timezone-aware UTC datetime
#                     obj["_fetched_at"] = datetime.now(timezone.utc)
#                     obj["_dataset"] = dataset_name
#                     obj["_source_url"] = url
#                     obj["_data_date"] = data_date if data_date else current_date_string
#                     json_data.append(obj)
#                     line_count += 1
                    
#                     # Batch insert to manage memory for large datasets
#                     if len(json_data) >= batch_size:
#                         collection.insert_many(json_data)
#                         logging.debug(f"📦 Batch inserted {len(json_data)} records into '{dataset_name}'")
#                         json_data = []
                        
#                 except json.JSONDecodeError as e:
#                     logging.warning(f"⚠️ JSON decode error in {dataset_name}: {str(e)}")
#                     continue

#         # Insert any remaining records
#         if json_data:
#             collection.insert_many(json_data)
#             logging.debug(f"📦 Final batch inserted {len(json_data)} records into '{dataset_name}'")

#         # Create index on common fields for better query performance
#         try:
#             collection.create_index([("_dataset", pymongo.ASCENDING)])
#             collection.create_index([("_fetched_at", pymongo.DESCENDING)])
#             collection.create_index([("_data_date", pymongo.DESCENDING)])
#             indexes_created = True
#         except Exception as e:
#             logging.warning(f"⚠️ Could not create indexes for {dataset_name}: {e}")
#             indexes_created = False

#         # Log operation success - PASS data_date again to ensure it's saved
#         scraping_logger.log_operation_success(
#             operation_id=operation_id,
#             records_processed=line_count,
#             records_inserted=line_count,
#             records_deleted=records_deleted,
#             data_date=data_date if data_date else current_date_string,  # Pass data_date here
#             batch_size=batch_size,
#             indexes_created=indexes_created
#         )
        
#         logging.info(f"✅ Successfully processed {line_count} records for '{dataset_name}' "
#                     f"(data date: {data_date if data_date else 'latest'})")
#         return True, line_count, data_date, operation_id

#     except requests.exceptions.Timeout as e:
#         error_msg = f"Timeout error processing dataset '{dataset_name}'"
#         logging.error(f"⏰ {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg, timeout_seconds=timeout)
#         return False, 0, data_date, operation_id
#     except requests.exceptions.HTTPError as e:
#         error_msg = f"HTTP error {e.response.status_code} for dataset '{dataset_name}': {e}"
#         logging.error(f"🌐 {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg, http_status=e.response.status_code)
#         return False, 0, data_date, operation_id
#     except requests.exceptions.RequestException as e:
#         error_msg = f"Network error processing dataset '{dataset_name}': {str(e)}"
#         logging.error(f"🌐 {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg)
#         return False, 0, data_date, operation_id
#     except Exception as e:
#         error_msg = f"Error processing dataset '{dataset_name}': {str(e)}"
#         logging.error(f"❌ {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg)
#         return False, 0, data_date, operation_id

# def cleanup_stuck_operations():
#     """Find and mark operations that have been 'in_progress' for too long"""
#     try:
#         cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        
#         stuck_ops = db.scraping_operations.find({
#             "status": "in_progress",
#             "start_time": {"$lt": cutoff_time}
#         })
        
#         count = 0
#         for op in stuck_ops:
#             db.scraping_operations.update_one(
#                 {"_id": op["_id"]},
#                 {"$set": {
#                     "status": "abandoned",
#                     "end_time": datetime.now(timezone.utc),
#                     "error_message": "Operation abandoned - likely crashed or timed out",
#                     "duration_seconds": (datetime.now(timezone.utc) - op["start_time"]).total_seconds()
#                 }}
#             )
#             count += 1
#             logging.warning(f"🚨 Marked abandoned operation: {op['operation_id']}")
        
#         if count > 0:
#             logging.info(f"🧹 Cleaned up {count} stuck operations")
        
#         return count
#     except Exception as e:
#         logging.error(f"Error cleaning stuck operations: {e}")
#         return 0

# def main():
#     current_date = get_current_date_string()
#     total_datasets = len(DATASETS)
    
#     # Clean up stuck operations first
#     cleanup_stuck_operations()
    
#     # Fix missing data_dates in existing logs
#     scraping_logger.fix_missing_data_dates()
    
#     logging.info(f"🚀 Starting OpenSanctions sync job for {total_datasets} datasets on date {current_date}")
    
#     completed = 0
#     failed = []
#     total_records = 0
#     operation_ids = []
    
#     for dataset in DATASETS:
#         try:
#             start_time = time.time()
#             success, record_count, data_date, operation_id = fetch_and_store_dataset(dataset)
#             end_time = time.time()
#             duration = end_time - start_time
            
#             if operation_id:
#                 operation_ids.append(operation_id)
            
#             if success:
#                 completed += 1
#                 total_records += record_count
#             else:
#                 failed.append(dataset)
                
#             progress = (completed / total_datasets) * 100
#             status = "✅" if success else "❌"
#             data_info = f"(data: {data_date})" if data_date else ""
#             logging.info(f"📊 {status} Progress: {completed}/{total_datasets} ({progress:.1f}%) - "
#                         f"{dataset}: {record_count} records in {duration:.2f}s {data_info}")
            
#             # Small delay to be respectful to the server
#             time.sleep(1)
            
#         except Exception as e:
#             logging.error(f"💥 Critical error processing {dataset}: {str(e)}")
#             failed.append(dataset)
    
#     # Create daily summary after all operations
#     daily_summary = scraping_logger.create_daily_summary(current_date)
    
#     # Summary
#     logging.info(f"\n📈 SYNC SUMMARY for {current_date}")
#     logging.info(f"✅ Successfully processed: {completed}/{total_datasets} datasets")
#     logging.info(f"📊 Total records imported: {total_records:,}")
#     if failed:
#         logging.warning(f"❌ Failed datasets: {failed}")
#     else:
#         logging.info("🎉 All datasets processed successfully!")
    
#     if daily_summary:
#         logging.info(f"📋 Success rate: {daily_summary.get('success_rate', 0)}%")
#         logging.info(f"📅 Data dates used: {', '.join(daily_summary.get('data_dates_used', []))}")
    
#     # Save sync metadata (optional - keeping your existing flow)
#     sync_metadata = {
#         "sync_date": datetime.now(timezone.utc),
#         "data_date": current_date,
#         "total_datasets": total_datasets,
#         "successful_datasets": completed,
#         "failed_datasets": failed,
#         "total_records": total_records
#     }
    
#     db["sync_metadata"].insert_one(sync_metadata)
#     logging.info("💾 Sync metadata saved to database")
#     logging.info("OpenSanctions sync job finished.\n")

# def daily_sync():
#     """Main function to run as a daily cron job"""
#     logging.info("=" * 60)
#     logging.info("🕒 DAILY OPEN SANCTIONS SYNC STARTED")
#     logging.info("=" * 60)
    
#     # Clean up old logs (keep last 90 days) - runs daily
#     scraping_logger.cleanup_old_logs(days_to_keep=90)
    
#     main()
    
#     logging.info("=" * 60)
#     logging.info("🕒 DAILY OPEN SANCTIONS SYNC COMPLETED")
#     logging.info("=" * 60)

# def show_scraping_history(dataset_name: Optional[str] = None, limit: int = 20):
#     """Display scraping history in a readable format"""
#     history = scraping_logger.get_operation_history(dataset_name=dataset_name, limit=limit)
    
#     if not history:
#         print("📭 No scraping history found")
#         return
    
#     print(f"\n📊 SCRAPING HISTORY {'for ' + dataset_name if dataset_name else ''}")
#     print("=" * 120)
#     print(f"{'Operation ID':<30} {'Dataset':<20} {'Data Date':<12} {'Start Time':<20} {'Status':<12} {'Records':<10} {'Duration':<10}")
#     print("-" * 120)
    
#     for log in history:
#         operation_id_short = log['operation_id'][-20:] if len(log['operation_id']) > 20 else log['operation_id']
#         start_time = log['start_time'].strftime('%Y-%m-%d %H:%M') if isinstance(log['start_time'], datetime) else log['start_time'][:16]
#         duration = f"{log.get('duration_seconds', 0):.1f}s" if log.get('duration_seconds') else "N/A"
#         records = log.get('records_processed', 0)
#         data_date = log.get('data_date', 'N/A')
        
#         status_emoji = {
#             'success': '✅',
#             'failed': '❌',
#             'in_progress': '⏳',
#             'abandoned': '🚫'
#         }.get(log.get('status', ''), '❓')
        
#         print(f"{operation_id_short:<30} {log['dataset_name']:<20} {data_date:<12} {start_time:<20} "
#               f"{status_emoji} {log.get('status', 'unknown'):<10} {records:<10} {duration:<10}")
    
#     print("=" * 120)
#     print(f"Total operations: {len(history)}")

# def show_daily_summary(date_str: str = None):
#     """Display daily summary in readable format"""
#     if date_str is None:
#         date_str = datetime.now().strftime("%Y%m%d")
    
#     summary = scraping_logger.get_daily_summary(date_str)
    
#     if not summary:
#         print(f"📭 No daily summary found for date: {date_str}")
#         return
    
#     print(f"\n📅 DAILY SUMMARY for {date_str}")
#     print("=" * 70)
#     print(f"Total operations: {summary.get('total_operations', 0)}")
#     print(f"Successful: {summary.get('successful_operations', 0)}")
#     print(f"Failed: {summary.get('failed_operations', 0)}")
#     print(f"In Progress: {summary.get('in_progress_operations', 0)}")
#     print(f"Success rate: {summary.get('success_rate', 0)}%")
#     print(f"Total records processed: {summary.get('total_records_processed', 0):,}")
#     print(f"Total records inserted: {summary.get('total_records_inserted', 0):,}")
#     print(f"Average duration: {summary.get('avg_duration_seconds', 0):.1f}s")
#     print(f"Data dates used: {', '.join(summary.get('data_dates_used', []))}")
    
#     if summary.get('failed_datasets'):
#         print(f"\n❌ Failed datasets:")
#         for failed in summary['failed_datasets']:
#             print(f"  - {failed.get('name', 'Unknown')}: {failed.get('error', 'No error message')}")
#     print("=" * 70)

# def show_dataset_statistics(dataset_name: str):
#     """Display detailed statistics for a dataset"""
#     stats = scraping_logger.get_dataset_statistics(dataset_name)
    
#     if not stats:
#         print(f"📭 No statistics found for dataset: {dataset_name}")
#         return
    
#     print(f"\n📈 DATASET STATISTICS: {dataset_name}")
#     print("=" * 70)
#     print(f"Total operations: {stats.get('total_operations', 0)}")
#     print(f"Successful: {stats.get('successful_operations', 0)}")
#     print(f"Failed: {stats.get('failed_operations', 0)}")
#     print(f"Success rate: {stats.get('success_rate', 0)}%")
#     print(f"Total records processed: {stats.get('total_records_processed', 0):,}")
#     print(f"Total records inserted: {stats.get('total_records_inserted', 0):,}")
#     print(f"Latest data date: {stats.get('latest_data_date', 'N/A')}")
#     last_scraped = stats.get('last_scraped', 'Never')
#     if isinstance(last_scraped, datetime):
#         last_scraped = last_scraped.strftime('%Y-%m-%d %H:%M:%S')
#     print(f"Last scraped: {last_scraped}")
#     print(f"Average duration: {stats.get('avg_duration_seconds', 0):.1f} seconds")
#     print("=" * 70)

# def update_all_missing_data_dates():
#     """Update all existing operations with missing data_dates"""
#     print("🔧 Updating all operations with missing data_dates...")
#     fixed_count = scraping_logger.fix_missing_data_dates()
#     print(f"✅ Fixed {fixed_count} operations")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='OpenSanctions Data Sync with Logging')
#     parser.add_argument('--show-history', type=str, nargs='?', const='all',
#                        help='Show scraping history (optional: dataset name)')
#     parser.add_argument('--daily-summary', type=str, nargs='?', const='today',
#                        help='Show daily summary (optional: date in YYYYMMDD format)')
#     parser.add_argument('--stats', type=str, 
#                        help='Show statistics for a specific dataset')
#     parser.add_argument('--cleanup', type=int, default=None,
#                        help='Clean up logs older than specified days (default: 90)')
#     parser.add_argument('--fix-data-dates', action='store_true',
#                        help='Fix missing data_dates in existing logs')
    
#     args = parser.parse_args()
    
#     if args.show_history:
#         if args.show_history == 'all':
#             show_scraping_history()
#         else:
#             show_scraping_history(dataset_name=args.show_history)
#     elif args.daily_summary:
#         if args.daily_summary == 'today':
#             show_daily_summary()
#         else:
#             show_daily_summary(date_str=args.daily_summary)
#     elif args.stats:
#         show_dataset_statistics(args.stats)
#     elif args.cleanup:
#         deleted_count = scraping_logger.cleanup_old_logs(days_to_keep=args.cleanup)
#         print(f"🧹 Cleaned up {deleted_count} old log entries")
#     elif args.fix_data_dates:
#         update_all_missing_data_dates()
#     else:
#         # Run the normal sync
#         daily_sync()










import requests
import pymongo
import json
import logging
from datetime import datetime, timezone, timedelta
import time
import os
from typing import Dict, List, Optional
import argparse
import re
import sys

# --- Logging Setup ---
log_file = "opensanctions_sync.log"

# Detect if running in Windows CMD and disable emojis
is_windows = sys.platform.startswith('win')

# Create a custom formatter that handles Windows CMD encoding issues
class SafeFormatter(logging.Formatter):
    def format(self, record):
        # Replace emojis with text on Windows
        if is_windows:
            emoji_replacements = {
                '✅': '[OK]',
                '❌': '[ERROR]',
                '⚠️': '[WARNING]',
                '🔄': '[SYNC]',
                '📦': '[INSERT]',
                '📊': '[PROGRESS]',
                '🚀': '[START]',
                '🎉': '[SUCCESS]',
                '💾': '[SAVE]',
                '🧹': '[CLEANUP]',
                '🔧': '[FIX]',
                '📋': '[SUMMARY]',
                '📅': '[DATE]',
                '📈': '[STATS]',
                '📭': '[EMPTY]',
                '⏰': '[TIMEOUT]',
                '🌐': '[NETWORK]',
                '🔍': '[DEBUG]',
                '🗑️': '[DELETE]',
                '⬇️': '[DOWNLOAD]',
                '🚨': '[ALERT]',
                '⏳': '[WAIT]',
                '📝': '[LOG]',
                '🕒': '[TIME]',
            }
            if hasattr(record, 'msg') and record.msg:
                for emoji, replacement in emoji_replacements.items():
                    record.msg = record.msg.replace(emoji, replacement)
        
        return super().format(record)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[]
)

# Create handlers
file_handler = logging.FileHandler(log_file, encoding='utf-8')
console_handler = logging.StreamHandler()

# Use safe formatter
formatter = SafeFormatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to root logger
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --- MongoDB Setup ---
client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["auth_tutorial"]
db = client["complyfor_db"] 

# === Dataset Full Names Dictionary ===
DATASET_FULL_NAMES = {
    "pl_mswia_sanctions": "Poland Ministry of National Defense (MSWIA) Sanctions",
    "be_fod_sanctions": "Belgium Federal Public Service Foreign Affairs Sanctions",
    "au_dfat_sanctions": "Australia Department of Foreign Affairs and Trade (DFAT) Sanctions",
    "kg_fiu_national": "Kyrgyzstan Financial Intelligence Unit National Sanctions List",
    "in_mha_banned": "India Ministry of Home Affairs Banned List",
    "jp_mof_sanctions": "Japan Ministry of Finance Sanctions",
    "ebrd_ineligible": "European Bank for Reconstruction and Development Ineligible Firms List",
    "ca_listed_terrorists": "Canada Listed Terrorist Entities",
    "eu_europol_wanted": "European Union Europol Wanted List",
    "az_fiu_sanctions": "Azerbaijan Financial Intelligence Unit Sanctions",
    "us_occ_enfact": "U.S. Office of the Comptroller of the Currency (OCC) Enforcement Actions",
    "eu_sanctions_map": "European Union Sanctions Map",
    "ch_seco_sanctions": "Switzerland State Secretariat for Economic Affairs (SECO) Sanctions",
    "gb_hmt_sanctions": "United Kingdom HM Treasury Sanctions",
    "ca_facfoa": "Canada FINTRAC Form (Financial Transactions and Reports Analysis Centre)",
    "ru_acf_bribetakers": "Russia Anti-Corruption Foundation Bribetakers List",
    "ua_nsdc_sanctions": "Ukraine National Security and Defense Council Sanctions",
    "eu_meps": "European Union Members of the European Parliament (MEPs)",
    "iadb_sanctions": "Inter-American Development Bank Sanctions List",
    "adb_sanctions": "Asian Development Bank Sanctions List",
    "ru_nsd_isin": "Russia National Settlement Depository (NSD) ISIN Database",
    "un_sc_sanctions": "United Nations Security Council Sanctions",
    "md_rise_profiles": "Moldova Risk and Insecurity Situations Evaluation (RISE) Profiles",
    "us_fbi_most_wanted": "U.S. Federal Bureau of Investigation (FBI) Most Wanted",
    "ca_dfatd_sema_sanctions": "Canada DFATD SEMA Sanctions",
    "ae_local_terrorists": "United Arab Emirates Local Terrorists List",
    "us_cuba_sanctions": "U.S. Cuba Sanctions",
    "sy_obsalytics_opensyr": "Syria Obsalytics OpenSYR Database",
    "lt_fiu_freezes": "Lithuania Financial Intelligence Unit Freezes List",
    "ar_repet": "Argentina Register of Public Officials with Conflict of Interest",
    "za_fic_sanctions": "South Africa Financial Intelligence Centre Sanctions",
    "ru_fedsfm_wmd": "Russia Fedsfm Weapons of Mass Destruction (WMD) List",
    "interpol_red_notices": "Interpol Red Notices",
    "us_ofac_sdn": "U.S. Office of Foreign Assets Control (OFAC) SDN List",
    "eu_fsf": "European Union Financial Sanctions Framework (FSF)",
    "sg_terrorists": "Singapore Terrorists List",
    "fr_tresor_gels_avoir": "France Ministry of Economy and Finance Freezing of Assets (GEL/AVOIR) List",
    "nz_russia_sanctions": "New Zealand Russia Sanctions",
    "bg_omnio_poi": "Bulgaria OMNIO Persons of Interest (POI) Database",
    "us_cia_world_leaders": "U.S. Central Intelligence Agency (CIA) World Leaders",
    "everypolitician": "EveryPolitician Open Data Project",
    "eu_cor_members": "European Union Committee of the Regions Members",
    "worldbank_debarred": "World Bank Debarred Firms List",
    "qa_nctc_sanctions": "Qatar National Counter-Terrorism Committee (NCTC) Sanctions",
    "nl_most_wanted": "Netherlands Most Wanted List",
    "md_interdictie": "Moldova Interdiction List",
    "gb_coh_disqualified": "United Kingdom Companies House Disqualified Directors",
    "us_ofac_cons": "U.S. Office of Foreign Assets Control (OFAC) Consolidated Sanctions List",
    "afdb_sanctions": "African Development Bank Sanctions List",
    "eu_travel_bans": "European Union Travel Bans List",
    "ua_sfms_blacklist": "Ukraine State Financial Monitoring Service (SFMS) Blacklist",
    "il_mod_terrorists": "Israel Ministry of Defense (MOD) Terrorists List",
}

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

def ensure_timezone_aware(dt):
    """Ensure datetime is timezone aware (UTC)"""
    if dt is None:
        return None
    if isinstance(dt, str):
        # Parse string to datetime
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    
    if dt.tzinfo is None:
        # Make naive datetime timezone aware (UTC)
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt

def get_dataset_full_name(dataset_code):
    """Get the full name for a dataset code"""
    return DATASET_FULL_NAMES.get(dataset_code, dataset_code)

class ScrapingLogger:
    """Manages scraping operation logs in MongoDB - Hybrid Approach"""
    
    def __init__(self, db):
        self.db = db
        self.operations_collection = db["scraping_operations"]
        self.daily_summary_collection = db["scraping_daily_summary"]
        self._ensure_indexes()
        logging.info("[OK] ScrapingLogger initialized")
    
    def _ensure_indexes(self):
        """Create optimized indexes for both collections"""
        try:
            # Indexes for individual operations
            self.operations_collection.create_index([("date", pymongo.DESCENDING)])
            self.operations_collection.create_index([("dataset_name", pymongo.ASCENDING)])
            self.operations_collection.create_index([("status", pymongo.ASCENDING)])
            self.operations_collection.create_index([("operation_id", pymongo.ASCENDING)], unique=True)
            self.operations_collection.create_index([("data_date", pymongo.DESCENDING)])
            self.operations_collection.create_index([("dataset_full_name", pymongo.ASCENDING)])  # New index
            
            # Indexes for daily summaries
            self.daily_summary_collection.create_index([("date", pymongo.DESCENDING)], unique=True)
            
            logging.debug("[OK] Created optimized indexes for logging collections")
        except Exception as e:
            logging.error(f"[ERROR] Error creating indexes: {e}")
    
    def log_operation_start(self, dataset_name: str, collection_name: str, 
                           source_url: str = None, data_date: str = None) -> str:
        """Log the start of a scraping operation and return operation ID"""
        try:
            operation_id = f"{dataset_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
            # Extract data_date from URL if not provided
            if not data_date and source_url:
                match = re.search(r'datasets/(\d{8})/', source_url)
                if match:
                    data_date = match.group(1)
            
            # Always use timezone-aware datetime
            current_time = datetime.now(timezone.utc)
            
            # Get dataset full name
            dataset_full_name = get_dataset_full_name(dataset_name)
            
            operation_log = {
                "operation_id": operation_id,
                "dataset_name": dataset_name,
                "dataset_full_name": dataset_full_name,  # NEW FIELD
                "collection_name": collection_name,
                "date": current_time.strftime("%Y%m%d"),
                "start_time": current_time,
                "status": "in_progress",
                "records_processed": 0,
                "records_inserted": 0,
                "records_deleted": 0,
                "source_url": source_url,
                "data_date": data_date,
                "metadata": {
                    "host": os.uname().nodename if hasattr(os, 'uname') else "unknown",
                    "python_version": os.sys.version,
                    "script_version": "1.0.0"
                }
            }
            
            result = self.operations_collection.insert_one(operation_log)
            logging.debug(f"[LOG] Started operation: {operation_id} (data_date: {data_date})")
            return operation_id
        except Exception as e:
            logging.error(f"[ERROR] Error logging operation start: {e}")
            return f"error_{int(time.time())}"
    
    def log_operation_success(self, operation_id: str, records_processed: int, 
                            records_inserted: int, records_deleted: int = 0,
                            data_date: str = None, **kwargs):
        """Log successful completion of a scraping operation"""
        try:
            operation = self.operations_collection.find_one({"operation_id": operation_id})
            if not operation:
                logging.error(f"[WARNING] Operation {operation_id} not found in database")
                return
            
            start_time = ensure_timezone_aware(operation.get("start_time"))
            end_time = datetime.now(timezone.utc)
            
            if start_time:
                duration = (end_time - start_time).total_seconds()
            else:
                duration = 0
            
            # Use data_date from parameters or keep existing one
            final_data_date = data_date if data_date else operation.get("data_date")
            
            update_data = {
                "end_time": end_time,
                "status": "success",
                "records_processed": records_processed,
                "records_inserted": records_inserted,
                "records_deleted": records_deleted,
                "duration_seconds": round(duration, 2),
                "data_date": final_data_date
            }
            
            # Update metadata
            current_metadata = operation.get("metadata", {})
            current_metadata.update(kwargs)
            update_data["metadata"] = current_metadata
            
            result = self.operations_collection.update_one(
                {"operation_id": operation_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logging.info(f"[OK] Completed operation: {operation_id} ({records_processed} records, data_date: {final_data_date})")
            else:
                logging.warning(f"[WARNING] No document updated for operation: {operation_id}")
                
        except Exception as e:
            logging.error(f"[ERROR] Error logging operation success for {operation_id}: {e}")
    
    def log_operation_failure(self, operation_id: str, error_message: str, **kwargs):
        """Log failed scraping operation"""
        try:
            operation = self.operations_collection.find_one({"operation_id": operation_id})
            if not operation:
                logging.error(f"[WARNING] Operation {operation_id} not found in database")
                return
            
            start_time = ensure_timezone_aware(operation.get("start_time"))
            end_time = datetime.now(timezone.utc)
            
            if start_time:
                duration = (end_time - start_time).total_seconds()
            else:
                duration = 0
            
            update_data = {
                "end_time": end_time,
                "status": "failed",
                "error_message": error_message[:500],
                "duration_seconds": round(duration, 2)
            }
            
            # Update metadata
            current_metadata = operation.get("metadata", {})
            current_metadata.update(kwargs)
            update_data["metadata"] = current_metadata
            
            result = self.operations_collection.update_one(
                {"operation_id": operation_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logging.info(f"[ERROR] Marked operation as failed: {operation_id} (duration: {duration:.2f}s)")
            else:
                logging.warning(f"[WARNING] No document updated for failed operation: {operation_id}")
                
        except Exception as e:
            logging.error(f"[ERROR] Error logging operation failure for {operation_id}: {e}")
    
    def create_daily_summary(self, date_str: str = None) -> Dict:
        """Create or update daily summary from all operations of that day"""
        if date_str is None:
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        
        try:
            # Aggregate all operations for this date
            pipeline = [
                {"$match": {"date": date_str}},
                {"$group": {
                    "_id": "$date",
                    "total_operations": {"$sum": 1},
                    "successful_operations": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                    "failed_operations": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
                    "in_progress_operations": {"$sum": {"$cond": [{"$eq": ["$status", "in_progress"]}, 1, 0]}},
                    "total_records_processed": {"$sum": "$records_processed"},
                    "total_records_inserted": {"$sum": "$records_inserted"},
                    "total_records_deleted": {"$sum": "$records_deleted"},
                    "avg_duration_seconds": {"$avg": "$duration_seconds"},
                    "max_duration_seconds": {"$max": "$duration_seconds"},
                    "min_duration_seconds": {"$min": "$duration_seconds"},
                    "operations": {"$push": {
                        "operation_id": "$operation_id",
                        "dataset_name": "$dataset_name",
                        "dataset_full_name": "$dataset_full_name",  # NEW FIELD
                        "status": "$status",
                        "data_date": "$data_date",
                        "records_processed": "$records_processed",
                        "duration_seconds": "$duration_seconds",
                        "error_message": "$error_message"
                    }},
                    "data_dates_used": {"$addToSet": "$data_date"},
                    "failed_datasets": {
                        "$push": {
                            "$cond": [
                                {"$eq": ["$status", "failed"]},
                                {"name": "$dataset_name", "full_name": "$dataset_full_name", "error": "$error_message"},
                                None
                            ]
                        }
                    },
                    "first_operation": {"$min": "$start_time"},
                    "last_operation": {"$max": "$end_time"}
                }},
                {"$project": {
                    "date": "$_id",
                    "total_operations": 1,
                    "successful_operations": 1,
                    "failed_operations": 1,
                    "in_progress_operations": 1,
                    "total_records_processed": 1,
                    "total_records_inserted": 1,
                    "total_records_deleted": 1,
                    "success_rate": {
                        "$cond": [
                            {"$gt": ["$total_operations", 0]},
                            {"$round": [
                                {"$multiply": [
                                    {"$divide": ["$successful_operations", "$total_operations"]},
                                    100
                                ]},
                                2
                            ]},
                            0
                        ]
                    },
                    "avg_duration_seconds": {"$ifNull": [{"$round": ["$avg_duration_seconds", 2]}, 0]},
                    "max_duration_seconds": {"$ifNull": [{"$round": ["$max_duration_seconds", 2]}, 0]},
                    "min_duration_seconds": {"$ifNull": [{"$round": ["$min_duration_seconds", 2]}, 0]},
                    "total_duration_hours": {
                        "$cond": [
                            {"$and": [{"$ne": ["$first_operation", None]}, {"$ne": ["$last_operation", None]}]},
                            {"$round": [{
                                "$divide": [{
                                    "$subtract": ["$last_operation", "$first_operation"]
                                }, 3600000]
                            }, 2]},
                            0
                        ]
                    },
                    "operations": {"$slice": ["$operations", 100]},
                    "data_dates_used": {
                        "$filter": {
                            "input": "$data_dates_used",
                            "as": "date",
                            "cond": {"$ne": ["$$date", None]}
                        }
                    },
                    "failed_datasets": {
                        "$filter": {
                            "input": "$failed_datasets",
                            "as": "failed",
                            "cond": {"$ne": ["$$failed", None]}
                        }
                    },
                    "generated_at": datetime.now(timezone.utc)
                }}
            ]
            
            result = list(self.operations_collection.aggregate(pipeline))
            
            if result:
                summary = result[0]
                # Clean up the operations list
                if "operations" in summary:
                    for op in summary["operations"]:
                        if op.get("error_message") is None:
                            op.pop("error_message", None)
                
                # Upsert daily summary
                self.daily_summary_collection.update_one(
                    {"date": date_str},
                    {"$set": summary},
                    upsert=True
                )
                
                logging.info(f"[SUMMARY] Created daily summary for {date_str}: "
                           f"{summary['successful_operations']}/{summary['total_operations']} successful")
                return summary
            
            logging.warning(f"[WARNING] No operations found for date {date_str}")
            return None
            
        except Exception as e:
            logging.error(f"[ERROR] Error creating daily summary: {e}")
            return None
    
    def get_daily_summary(self, date_str: str) -> Optional[Dict]:
        """Get daily summary by date"""
        return self.daily_summary_collection.find_one({"date": date_str})
    
    def get_operation_history(self, dataset_name: Optional[str] = None, 
                             days_back: int = 7, limit: int = 50) -> List[Dict]:
        """Get operation history with optional filters"""
        query = {}
        
        # Date filter
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
        query["date"] = {"$gte": cutoff_date}
        
        # Dataset filter
        if dataset_name:
            query["dataset_name"] = dataset_name
        
        return list(self.operations_collection.find(query)
                   .sort("start_time", pymongo.DESCENDING)
                   .limit(limit))
    
    def get_dataset_statistics(self, dataset_name: str, days_back: int = 30) -> Dict:
        """Get statistics for a specific dataset"""
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
        
        try:
            pipeline = [
                {"$match": {
                    "dataset_name": dataset_name,
                    "date": {"$gte": cutoff_date},
                    "status": {"$in": ["success", "failed"]}
                }},
                {"$group": {
                    "_id": "$dataset_name",
                    "total_operations": {"$sum": 1},
                    "successful_operations": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                    "failed_operations": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
                    "total_records_processed": {"$sum": "$records_processed"},
                    "total_records_inserted": {"$sum": "$records_inserted"},
                    "latest_data_date": {"$max": "$data_date"},
                    "last_scraped": {"$max": "$end_time"},
                    "avg_duration_seconds": {"$avg": "$duration_seconds"},
                    "success_rate": {
                        "$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                    }
                }},
                {"$project": {
                    "dataset_name": "$_id",
                    "total_operations": 1,
                    "successful_operations": 1,
                    "failed_operations": 1,
                    "total_records_processed": 1,
                    "total_records_inserted": 1,
                    "latest_data_date": 1,
                    "last_scraped": 1,
                    "avg_duration_seconds": {"$ifNull": [{"$round": ["$avg_duration_seconds", 2]}, 0]},
                    "success_rate": {"$ifNull": [{"$round": [{"$multiply": ["$success_rate", 100]}, 2]}, 0]}
                }}
            ]
            
            result = list(self.operations_collection.aggregate(pipeline))
            return result[0] if result else {}
        except Exception as e:
            logging.error(f"[ERROR] Error getting dataset statistics: {e}")
            return {}
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Clean up logs older than specified days"""
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).strftime("%Y%m%d")
            
            # Delete old operations
            ops_result = self.operations_collection.delete_many({"date": {"$lt": cutoff_date}})
            
            # Delete old summaries
            summary_result = self.daily_summary_collection.delete_many({"date": {"$lt": cutoff_date}})
            
            logging.info(f"[CLEANUP] Cleaned up {ops_result.deleted_count} old operations and "
                        f"{summary_result.deleted_count} old summaries (older than {days_to_keep} days)")
            return ops_result.deleted_count + summary_result.deleted_count
        except Exception as e:
            logging.error(f"[ERROR] Error cleaning up old logs: {e}")
            return 0
    
    def fix_missing_data_dates(self):
        """Fix operations missing data_date by extracting from source_url"""
        try:
            operations = self.operations_collection.find({
                "data_date": {"$exists": False},
                "source_url": {"$exists": True, "$ne": None}
            })
            
            fixed_count = 0
            for op in operations:
                url = op.get("source_url", "")
                match = re.search(r'datasets/(\d{8})/', url)
                if match:
                    data_date = match.group(1)
                    self.operations_collection.update_one(
                        {"_id": op["_id"]},
                        {"$set": {"data_date": data_date}}
                    )
                    fixed_count += 1
                    logging.debug(f"[FIX] Fixed data_date for {op['operation_id']}: {data_date}")
            
            if fixed_count > 0:
                logging.info(f"[FIX] Fixed {fixed_count} operations missing data_date")
            
            return fixed_count
        except Exception as e:
            logging.error(f"[ERROR] Error fixing missing data_dates: {e}")
            return 0
    
    def fix_missing_full_names(self):
        """Fix operations missing dataset_full_name"""
        try:
            operations = self.operations_collection.find({
                "dataset_full_name": {"$exists": False},
                "dataset_name": {"$exists": True}
            })
            
            fixed_count = 0
            for op in operations:
                dataset_name = op.get("dataset_name")
                if dataset_name:
                    dataset_full_name = get_dataset_full_name(dataset_name)
                    self.operations_collection.update_one(
                        {"_id": op["_id"]},
                        {"$set": {"dataset_full_name": dataset_full_name}}
                    )
                    fixed_count += 1
                    logging.debug(f"[FIX] Added full name for {dataset_name}: {dataset_full_name}")
            
            if fixed_count > 0:
                logging.info(f"[FIX] Added full names to {fixed_count} operations")
            
            return fixed_count
        except Exception as e:
            logging.error(f"[ERROR] Error fixing missing full names: {e}")
            return 0

# Initialize the scraping logger globally
scraping_logger = ScrapingLogger(db)

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
    except requests.RequestException as e:
        logging.debug(f"URL check failed: {e}")
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
            logging.info(f"[OK] Found data for {dataset_name} on date: {date_string}")
            return date_string, url
    
    # If no recent data found, try the 'latest' endpoint as fallback
    fallback_url = f"https://data.opensanctions.org/datasets/latest/{dataset_name}/targets.nested.json"
    logging.warning(f"[WARNING] No recent dated data found for {dataset_name}, using fallback: {fallback_url}")
    return None, fallback_url

def fetch_and_store_dataset(dataset_name):
    """Fetch and store dataset with comprehensive logging"""
    current_date_string = get_current_date_string()
    
    # Find the latest available data
    data_date, url = find_latest_available_date(dataset_name)
    if data_date:
        logging.info(f"[SYNC] Downloading {dataset_name} from {url} (data date: {data_date})")
    else:
        logging.info(f"[SYNC] Downloading {dataset_name} from {url} (using latest endpoint)")
    
    # Log operation start
    operation_id = scraping_logger.log_operation_start(
        dataset_name=dataset_name,
        collection_name=dataset_name,
        source_url=url,
        data_date=data_date
    )
    
    try:
        # Increase timeout for large datasets
        timeout = 300
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        collection = db[dataset_name]
        # Clear existing data for this dataset
        delete_result = collection.delete_many({})
        records_deleted = delete_result.deleted_count
        
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
                    obj["_dataset"] = dataset_name
                    obj["_source_url"] = url
                    obj["_data_date"] = data_date if data_date else current_date_string
                    json_data.append(obj)
                    line_count += 1
                    
                    # Batch insert to manage memory for large datasets
                    if len(json_data) >= batch_size:
                        collection.insert_many(json_data)
                        logging.debug(f"[INSERT] Batch inserted {len(json_data)} records into '{dataset_name}'")
                        json_data = []
                        
                except json.JSONDecodeError as e:
                    logging.warning(f"[WARNING] JSON decode error in {dataset_name}: {str(e)}")
                    continue

        # Insert any remaining records
        if json_data:
            collection.insert_many(json_data)
            logging.debug(f"[INSERT] Final batch inserted {len(json_data)} records into '{dataset_name}'")

        # Create index on common fields for better query performance
        try:
            collection.create_index([("_dataset", pymongo.ASCENDING)])
            collection.create_index([("_fetched_at", pymongo.DESCENDING)])
            collection.create_index([("_data_date", pymongo.DESCENDING)])
            indexes_created = True
        except Exception as e:
            logging.warning(f"[WARNING] Could not create indexes for {dataset_name}: {e}")
            indexes_created = False

        # Log operation success
        scraping_logger.log_operation_success(
            operation_id=operation_id,
            records_processed=line_count,
            records_inserted=line_count,
            records_deleted=records_deleted,
            data_date=data_date if data_date else current_date_string,
            batch_size=batch_size,
            indexes_created=indexes_created
        )
        
        logging.info(f"[OK] Successfully processed {line_count} records for '{dataset_name}' "
                    f"(data date: {data_date if data_date else 'latest'})")
        return True, line_count, data_date, operation_id

    except requests.exceptions.Timeout as e:
        error_msg = f"Timeout error processing dataset '{dataset_name}'"
        logging.error(f"[TIMEOUT] {error_msg}")
        scraping_logger.log_operation_failure(operation_id, error_msg, timeout_seconds=timeout)
        return False, 0, data_date, operation_id
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error {e.response.status_code} for dataset '{dataset_name}': {e}"
        logging.error(f"[NETWORK] {error_msg}")
        scraping_logger.log_operation_failure(operation_id, error_msg, http_status=e.response.status_code)
        return False, 0, data_date, operation_id
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error processing dataset '{dataset_name}': {str(e)}"
        logging.error(f"[NETWORK] {error_msg}")
        scraping_logger.log_operation_failure(operation_id, error_msg)
        return False, 0, data_date, operation_id
    except Exception as e:
        error_msg = f"Error processing dataset '{dataset_name}': {str(e)}"
        logging.error(f"[ERROR] {error_msg}")
        scraping_logger.log_operation_failure(operation_id, error_msg)
        return False, 0, data_date, operation_id

def cleanup_stuck_operations():
    """Find and mark operations that have been 'in_progress' for too long"""
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        # Ensure cutoff_time is timezone aware
        if cutoff_time.tzinfo is None:
            cutoff_time = cutoff_time.replace(tzinfo=timezone.utc)
        
        stuck_ops = db.scraping_operations.find({
            "status": "in_progress",
            "start_time": {"$lt": cutoff_time}
        })
        
        count = 0
        for op in stuck_ops:
            # Ensure start_time is timezone aware for calculation
            start_time = ensure_timezone_aware(op.get("start_time"))
            end_time = datetime.now(timezone.utc)
            
            if start_time:
                duration = (end_time - start_time).total_seconds()
            else:
                duration = 0
            
            db.scraping_operations.update_one(
                {"_id": op["_id"]},
                {"$set": {
                    "status": "abandoned",
                    "end_time": end_time,
                    "error_message": "Operation abandoned - likely crashed or timed out",
                    "duration_seconds": round(duration, 2)
                }}
            )
            count += 1
            logging.warning(f"[ALERT] Marked abandoned operation: {op['operation_id']}")
        
        if count > 0:
            logging.info(f"[CLEANUP] Cleaned up {count} stuck operations")
        
        return count
    except Exception as e:
        logging.error(f"Error cleaning stuck operations: {e}")
        return 0

def main():
    current_date = get_current_date_string()
    total_datasets = len(DATASETS)
    
    # Clean up stuck operations first
    cleanup_stuck_operations()
    
    # Fix missing data_dates in existing logs
    scraping_logger.fix_missing_data_dates()
    
    # Fix missing full names in existing logs
    scraping_logger.fix_missing_full_names()
    
    logging.info(f"[START] Starting OpenSanctions sync job for {total_datasets} datasets on date {current_date}")
    
    completed = 0
    failed = []
    total_records = 0
    operation_ids = []
    
    for dataset in DATASETS:
        try:
            start_time = time.time()
            success, record_count, data_date, operation_id = fetch_and_store_dataset(dataset)
            end_time = time.time()
            duration = end_time - start_time
            
            if operation_id:
                operation_ids.append(operation_id)
            
            if success:
                completed += 1
                total_records += record_count
            else:
                failed.append(dataset)
                
            progress = (completed / total_datasets) * 100
            status = "[OK]" if success else "[ERROR]"
            data_info = f"(data: {data_date})" if data_date else ""
            logging.info(f"[PROGRESS] {status} Progress: {completed}/{total_datasets} ({progress:.1f}%) - "
                        f"{dataset}: {record_count} records in {duration:.2f}s {data_info}")
            
            # Small delay to be respectful to the server
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"[ALERT] Critical error processing {dataset}: {str(e)}")
            failed.append(dataset)
    
    # Create daily summary after all operations
    try:
        daily_summary = scraping_logger.create_daily_summary(current_date)
    except Exception as e:
        logging.error(f"[ERROR] Failed to create daily summary: {e}")
        daily_summary = None
    
    # Summary
    logging.info(f"\n[STATS] SYNC SUMMARY for {current_date}")
    logging.info(f"[OK] Successfully processed: {completed}/{total_datasets} datasets")
    logging.info(f"[STATS] Total records imported: {total_records:,}")
    if failed:
        logging.warning(f"[ERROR] Failed datasets: {failed}")
    else:
        logging.info("[SUCCESS] All datasets processed successfully!")
    
    if daily_summary:
        logging.info(f"[SUMMARY] Success rate: {daily_summary.get('success_rate', 0)}%")
        logging.info(f"[DATE] Data dates used: {', '.join(daily_summary.get('data_dates_used', []))}")
    
    # Save sync metadata
    sync_metadata = {
        "sync_date": datetime.now(timezone.utc),
        "data_date": current_date,
        "total_datasets": total_datasets,
        "successful_datasets": completed,
        "failed_datasets": failed,
        "total_records": total_records
    }
    
    try:
        db["sync_metadata"].insert_one(sync_metadata)
        logging.info("[SAVE] Sync metadata saved to database")
    except Exception as e:
        logging.error(f"[ERROR] Failed to save sync metadata: {e}")
    
    logging.info("OpenSanctions sync job finished.\n")

def daily_sync():
    """Main function to run as a daily cron job"""
    logging.info("=" * 60)
    logging.info("[TIME] DAILY OPEN SANCTIONS SYNC STARTED")
    logging.info("=" * 60)
    
    # Clean up old logs (keep last 90 days) - runs daily
    scraping_logger.cleanup_old_logs(days_to_keep=90)
    
    main()
    
    logging.info("=" * 60)
    logging.info("[TIME] DAILY OPEN SANCTIONS SYNC COMPLETED")
    logging.info("=" * 60)

# Helper functions for manual use
def show_scraping_history(dataset_name: Optional[str] = None, limit: int = 20):
    """Display scraping history in a readable format"""
    history = scraping_logger.get_operation_history(dataset_name=dataset_name, limit=limit)
    
    if not history:
        print("[EMPTY] No scraping history found")
        return
    
    print(f"\n[STATS] SCRAPING HISTORY {'for ' + dataset_name if dataset_name else ''}")
    print("=" * 140)
    print(f"{'Operation ID':<30} {'Dataset':<20} {'Full Name':<40} {'Data Date':<12} {'Start Time':<20} {'Status':<12} {'Records':<10} {'Duration':<10}")
    print("-" * 140)
    
    for log in history:
        operation_id_short = log['operation_id'][-20:] if len(log['operation_id']) > 20 else log['operation_id']
        start_time = log['start_time'].strftime('%Y-%m-%d %H:%M') if isinstance(log['start_time'], datetime) else log['start_time'][:16]
        duration = f"{log.get('duration_seconds', 0):.1f}s" if log.get('duration_seconds') else "N/A"
        records = log.get('records_processed', 0)
        data_date = log.get('data_date', 'N/A')
        full_name = log.get('dataset_full_name', 'N/A')
        
        # Truncate full name if too long
        if len(full_name) > 35:
            full_name = full_name[:32] + "..."
        
        status_text = {
            'success': 'SUCCESS',
            'failed': 'FAILED',
            'in_progress': 'IN_PROGRESS',
            'abandoned': 'ABANDONED'
        }.get(log.get('status', ''), 'UNKNOWN')
        
        print(f"{operation_id_short:<30} {log['dataset_name']:<20} {full_name:<40} {data_date:<12} {start_time:<20} "
              f"{status_text:<12} {records:<10} {duration:<10}")
    
    print("=" * 140)
    print(f"Total operations: {len(history)}")

def show_daily_summary(date_str: str = None):
    """Display daily summary in readable format"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    
    summary = scraping_logger.get_daily_summary(date_str)
    
    if not summary:
        print(f"[EMPTY] No daily summary found for date: {date_str}")
        return
    
    print(f"\n[DATE] DAILY SUMMARY for {date_str}")
    print("=" * 80)
    print(f"Total operations: {summary.get('total_operations', 0)}")
    print(f"Successful: {summary.get('successful_operations', 0)}")
    print(f"Failed: {summary.get('failed_operations', 0)}")
    print(f"In Progress: {summary.get('in_progress_operations', 0)}")
    print(f"Success rate: {summary.get('success_rate', 0)}%")
    print(f"Total records processed: {summary.get('total_records_processed', 0):,}")
    print(f"Total records inserted: {summary.get('total_records_inserted', 0):,}")
    print(f"Average duration: {summary.get('avg_duration_seconds', 0):.1f}s")
    print(f"Data dates used: {', '.join(summary.get('data_dates_used', []))}")
    
    if summary.get('failed_datasets'):
        print(f"\n[ERROR] Failed datasets:")
        for failed in summary['failed_datasets']:
            full_name = failed.get('full_name', 'Unknown')
            name = failed.get('name', 'Unknown')
            error = failed.get('error', 'No error message')
            print(f"  - {name}: {full_name}")
            print(f"    Error: {error}")
    print("=" * 80)

def show_dataset_statistics(dataset_name: str):
    """Display detailed statistics for a dataset"""
    stats = scraping_logger.get_dataset_statistics(dataset_name)
    
    if not stats:
        print(f"[EMPTY] No statistics found for dataset: {dataset_name}")
        return
    
    full_name = get_dataset_full_name(dataset_name)
    
    print(f"\n📈 DATASET STATISTICS: {dataset_name}")
    print(f"📋 Full Name: {full_name}")
    print("=" * 70)
    print(f"Total operations: {stats.get('total_operations', 0)}")
    print(f"Successful: {stats.get('successful_operations', 0)}")
    print(f"Failed: {stats.get('failed_operations', 0)}")
    print(f"Success rate: {stats.get('success_rate', 0)}%")
    print(f"Total records processed: {stats.get('total_records_processed', 0):,}")
    print(f"Total records inserted: {stats.get('total_records_inserted', 0):,}")
    print(f"Latest data date: {stats.get('latest_data_date', 'N/A')}")
    last_scraped = stats.get('last_scraped', 'Never')
    if isinstance(last_scraped, datetime):
        last_scraped = last_scraped.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Last scraped: {last_scraped}")
    print(f"Average duration: {stats.get('avg_duration_seconds', 0):.1f} seconds")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OpenSanctions Data Sync with Logging')
    parser.add_argument('--run', action='store_true', help='Run the sync job')
    parser.add_argument('--history', type=str, nargs='?', const='all',
                       help='Show scraping history (optional: dataset name)')
    parser.add_argument('--summary', type=str, nargs='?', const='today',
                       help='Show daily summary (optional: date in YYYYMMDD format)')
    parser.add_argument('--stats', type=str, 
                       help='Show statistics for a specific dataset')
    parser.add_argument('--fix-dates', action='store_true',
                       help='Fix missing data_dates in existing logs')
    parser.add_argument('--fix-fullnames', action='store_true',
                       help='Fix missing dataset_full_name in existing logs')
    
    args = parser.parse_args()
    
    if args.history:
        if args.history == 'all':
            show_scraping_history()
        else:
            show_scraping_history(dataset_name=args.history)
    elif args.summary:
        if args.summary == 'today':
            show_daily_summary()
        else:
            show_daily_summary(date_str=args.summary)
    elif args.stats:
        show_dataset_statistics(args.stats)
    elif args.fix_dates:
        fixed_count = scraping_logger.fix_missing_data_dates()
        print(f"[FIX] Fixed {fixed_count} operations with missing data dates")
    elif args.fix_fullnames:
        fixed_count = scraping_logger.fix_missing_full_names()
        print(f"[FIX] Fixed {fixed_count} operations with missing full names")
    elif args.run or len(sys.argv) == 1:  # Default to run if no arguments
        daily_sync()
    else:
        print("Usage: python script.py [OPTIONS]")
        print("\nOptions:")
        print("  --run               Run the sync job")
        print("  --history [NAME]    Show scraping history (optional: dataset name)")
        print("  --summary [DATE]    Show daily summary (optional: date in YYYYMMDD)")
        print("  --stats DATASET     Show statistics for a specific dataset")
        print("  --fix-dates         Fix missing data_dates in existing logs")
        print("  --fix-fullnames     Fix missing dataset_full_name in existing logs")






























# import requests
# import pymongo
# import json
# import logging
# from datetime import datetime, timezone, timedelta
# import time
# import os
# from typing import Dict, List, Optional
# import argparse
# import re
# import sys

# # --- Logging Setup ---
# log_file = "opensanctions_sync.log"

# # Detect if running in Windows CMD and disable emojis
# is_windows = sys.platform.startswith('win')

# # Create a custom formatter that handles Windows CMD encoding issues
# class SafeFormatter(logging.Formatter):
#     def format(self, record):
#         # Replace emojis with text on Windows
#         if is_windows:
#             emoji_replacements = {
#                 '✅': '[OK]',
#                 '❌': '[ERROR]',
#                 '⚠️': '[WARNING]',
#                 '🔄': '[SYNC]',
#                 '📦': '[INSERT]',
#                 '📊': '[PROGRESS]',
#                 '🚀': '[START]',
#                 '🎉': '[SUCCESS]',
#                 '💾': '[SAVE]',
#                 '🧹': '[CLEANUP]',
#                 '🔧': '[FIX]',
#                 '📋': '[SUMMARY]',
#                 '📅': '[DATE]',
#                 '📈': '[STATS]',
#                 '📭': '[EMPTY]',
#                 '⏰': '[TIMEOUT]',
#                 '🌐': '[NETWORK]',
#                 '🔍': '[DEBUG]',
#                 '🗑️': '[DELETE]',
#                 '⬇️': '[DOWNLOAD]',
#                 '🚨': '[ALERT]',
#                 '⏳': '[WAIT]',
#                 '📝': '[LOG]',
#                 '🕒': '[TIME]',
#             }
#             if hasattr(record, 'msg') and record.msg:
#                 for emoji, replacement in emoji_replacements.items():
#                     record.msg = record.msg.replace(emoji, replacement)
        
#         return super().format(record)

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[]
# )

# # Create handlers
# file_handler = logging.FileHandler(log_file, encoding='utf-8')
# console_handler = logging.StreamHandler()

# # Use safe formatter
# formatter = SafeFormatter("%(asctime)s [%(levelname)s] %(message)s")
# file_handler.setFormatter(formatter)
# console_handler.setFormatter(formatter)

# # Add handlers to root logger
# logger = logging.getLogger()
# logger.addHandler(file_handler)
# logger.addHandler(console_handler)

# # --- MongoDB Setup ---
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["auth_tutorial"]

# # === Dataset Configuration ===
# DATASETS = [
#     "pl_mswia_sanctions",           # 1.3Mb
#     "be_fod_sanctions",             # 12mb
#     "au_dfat_sanctions",            # 7.9 mb
#     "kg_fiu_national",              # 1.8 mb
#     "in_mha_banned",                # 233 kb
#     "jp_mof_sanctions",             # 8 mb
#     "ebrd_ineligible",              # 1.31 mb
#     "ca_listed_terrorists",         # 224 kb
#     "eu_europol_wanted",            # 28 kb
#     "az_fiu_sanctions",             # 35 kb
#     "us_occ_enfact",                # 6 mb
#     "eu_sanctions_map",             # 1.46 mb
#     "ch_seco_sanctions",            # 28 mb
#     "gb_hmt_sanctions",             # 14.81 Mb
#     "ca_facfoa",                    # 10 KB
#     "ru_acf_bribetakers",           # 8 MB
#     "ua_nsdc_sanctions",            # 114 MB
#     "eu_meps",                      # 1.81 MB
#     "iadb_sanctions",               # 1.28 MB
#     "adb_sanctions",                # 1.62 MB
#     "ru_nsd_isin",                  # 36 MB
#     "un_sc_sanctions",              # 2.9 MB
#     "md_rise_profiles",             # 1.47 MB
#     "us_fbi_most_wanted",           # 585 kb
#     "ca_dfatd_sema_sanctions",      # 8.7 mb
#     "ae_local_terrorists",          # 380 kb
#     "us_cuba_sanctions",            # 759 KB
#     "sy_obsalytics_opensyr",        # 22 MB
#     "lt_fiu_freezes",               # 58 KB
#     "ar_repet",                     # 1.64 MB
#     "za_fic_sanctions",             # 2.07 MB
#     "ru_fedsfm_wmd",                # 1.5 KB
#     "interpol_red_notices",         # 8.3 MB
#     "us_ofac_sdn",                  # 66 MB
#     "eu_fsf",                       # 13 MB
#     "sg_terrorists",                # 33 KB
#     "fr_tresor_gels_avoir",         # 20.81 MB
#     "nz_russia_sanctions",          # 4.7 MB
#     "bg_omnio_poi",                 # 715 KB
#     "us_cia_world_leaders",         # 7.5 MB
#     "everypolitician",              # 101.31 MB
#     "eu_cor_members",               # 887 KB
#     "worldbank_debarred",           # 2.27 MB
#     "qa_nctc_sanctions",            # 1 MB
#     "nl_most_wanted",               # 34.02 KB
#     "md_interdictie",               # 48 KB
#     "gb_coh_disqualified",          # 19.1 MB
#     "us_ofac_cons",                 # 2.94 MB
#     "afdb_sanctions",               # 1.11 MB
#     "eu_travel_bans",               # 7.87 MB
#     "ua_sfms_blacklist",            # 2.08 MB
#     "il_mod_terrorists",            # 2.05 MB
# ]

# def ensure_timezone_aware(dt):
#     """Ensure datetime is timezone aware (UTC)"""
#     if dt is None:
#         return None
#     if isinstance(dt, str):
#         # Parse string to datetime
#         try:
#             dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
#         except:
#             dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    
#     if dt.tzinfo is None:
#         # Make naive datetime timezone aware (UTC)
#         dt = dt.replace(tzinfo=timezone.utc)
    
#     return dt

# class ScrapingLogger:
#     """Manages scraping operation logs in MongoDB - Hybrid Approach"""
    
#     def __init__(self, db):
#         self.db = db
#         self.operations_collection = db["scraping_operations"]
#         self.daily_summary_collection = db["scraping_daily_summary"]
#         self._ensure_indexes()
#         logging.info("[OK] ScrapingLogger initialized")
    
#     def _ensure_indexes(self):
#         """Create optimized indexes for both collections"""
#         try:
#             # Indexes for individual operations
#             self.operations_collection.create_index([("date", pymongo.DESCENDING)])
#             self.operations_collection.create_index([("dataset_name", pymongo.ASCENDING)])
#             self.operations_collection.create_index([("status", pymongo.ASCENDING)])
#             self.operations_collection.create_index([("operation_id", pymongo.ASCENDING)], unique=True)
#             self.operations_collection.create_index([("data_date", pymongo.DESCENDING)])
            
#             # Indexes for daily summaries
#             self.daily_summary_collection.create_index([("date", pymongo.DESCENDING)], unique=True)
            
#             logging.debug("[OK] Created optimized indexes for logging collections")
#         except Exception as e:
#             logging.error(f"[ERROR] Error creating indexes: {e}")
    
#     def log_operation_start(self, dataset_name: str, collection_name: str, 
#                            source_url: str = None, data_date: str = None) -> str:
#         """Log the start of a scraping operation and return operation ID"""
#         try:
#             operation_id = f"{dataset_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
#             # Extract data_date from URL if not provided
#             if not data_date and source_url:
#                 match = re.search(r'datasets/(\d{8})/', source_url)
#                 if match:
#                     data_date = match.group(1)
            
#             # Always use timezone-aware datetime
#             current_time = datetime.now(timezone.utc)
            
#             operation_log = {
#                 "operation_id": operation_id,
#                 "dataset_name": dataset_name,
#                 "collection_name": collection_name,
#                 "date": current_time.strftime("%Y%m%d"),
#                 "start_time": current_time,
#                 "status": "in_progress",
#                 "records_processed": 0,
#                 "records_inserted": 0,
#                 "records_deleted": 0,
#                 "source_url": source_url,
#                 "data_date": data_date,
#                 "metadata": {
#                     "host": os.uname().nodename if hasattr(os, 'uname') else "unknown",
#                     "python_version": os.sys.version,
#                     "script_version": "1.0.0"
#                 }
#             }
            
#             result = self.operations_collection.insert_one(operation_log)
#             logging.debug(f"[LOG] Started operation: {operation_id} (data_date: {data_date})")
#             return operation_id
#         except Exception as e:
#             logging.error(f"[ERROR] Error logging operation start: {e}")
#             return f"error_{int(time.time())}"
    
#     def log_operation_success(self, operation_id: str, records_processed: int, 
#                             records_inserted: int, records_deleted: int = 0,
#                             data_date: str = None, **kwargs):
#         """Log successful completion of a scraping operation"""
#         try:
#             operation = self.operations_collection.find_one({"operation_id": operation_id})
#             if not operation:
#                 logging.error(f"[WARNING] Operation {operation_id} not found in database")
#                 return
            
#             start_time = ensure_timezone_aware(operation.get("start_time"))
#             end_time = datetime.now(timezone.utc)
            
#             if start_time:
#                 duration = (end_time - start_time).total_seconds()
#             else:
#                 duration = 0
            
#             # Use data_date from parameters or keep existing one
#             final_data_date = data_date if data_date else operation.get("data_date")
            
#             update_data = {
#                 "end_time": end_time,
#                 "status": "success",
#                 "records_processed": records_processed,
#                 "records_inserted": records_inserted,
#                 "records_deleted": records_deleted,
#                 "duration_seconds": round(duration, 2),
#                 "data_date": final_data_date
#             }
            
#             # Update metadata
#             current_metadata = operation.get("metadata", {})
#             current_metadata.update(kwargs)
#             update_data["metadata"] = current_metadata
            
#             result = self.operations_collection.update_one(
#                 {"operation_id": operation_id},
#                 {"$set": update_data}
#             )
            
#             if result.modified_count > 0:
#                 logging.info(f"[OK] Completed operation: {operation_id} ({records_processed} records, data_date: {final_data_date})")
#             else:
#                 logging.warning(f"[WARNING] No document updated for operation: {operation_id}")
                
#         except Exception as e:
#             logging.error(f"[ERROR] Error logging operation success for {operation_id}: {e}")
    
#     def log_operation_failure(self, operation_id: str, error_message: str, **kwargs):
#         """Log failed scraping operation"""
#         try:
#             operation = self.operations_collection.find_one({"operation_id": operation_id})
#             if not operation:
#                 logging.error(f"[WARNING] Operation {operation_id} not found in database")
#                 return
            
#             start_time = ensure_timezone_aware(operation.get("start_time"))
#             end_time = datetime.now(timezone.utc)
            
#             if start_time:
#                 duration = (end_time - start_time).total_seconds()
#             else:
#                 duration = 0
            
#             update_data = {
#                 "end_time": end_time,
#                 "status": "failed",
#                 "error_message": error_message[:500],
#                 "duration_seconds": round(duration, 2)
#             }
            
#             # Update metadata
#             current_metadata = operation.get("metadata", {})
#             current_metadata.update(kwargs)
#             update_data["metadata"] = current_metadata
            
#             result = self.operations_collection.update_one(
#                 {"operation_id": operation_id},
#                 {"$set": update_data}
#             )
            
#             if result.modified_count > 0:
#                 logging.info(f"[ERROR] Marked operation as failed: {operation_id} (duration: {duration:.2f}s)")
#             else:
#                 logging.warning(f"[WARNING] No document updated for failed operation: {operation_id}")
                
#         except Exception as e:
#             logging.error(f"[ERROR] Error logging operation failure for {operation_id}: {e}")
    
#     def create_daily_summary(self, date_str: str = None) -> Dict:
#         """Create or update daily summary from all operations of that day"""
#         if date_str is None:
#             date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        
#         try:
#             # Aggregate all operations for this date
#             pipeline = [
#                 {"$match": {"date": date_str}},
#                 {"$group": {
#                     "_id": "$date",
#                     "total_operations": {"$sum": 1},
#                     "successful_operations": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
#                     "failed_operations": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
#                     "in_progress_operations": {"$sum": {"$cond": [{"$eq": ["$status", "in_progress"]}, 1, 0]}},
#                     "total_records_processed": {"$sum": "$records_processed"},
#                     "total_records_inserted": {"$sum": "$records_inserted"},
#                     "total_records_deleted": {"$sum": "$records_deleted"},
#                     "avg_duration_seconds": {"$avg": "$duration_seconds"},
#                     "max_duration_seconds": {"$max": "$duration_seconds"},
#                     "min_duration_seconds": {"$min": "$duration_seconds"},
#                     "operations": {"$push": {
#                         "operation_id": "$operation_id",
#                         "dataset_name": "$dataset_name",
#                         "status": "$status",
#                         "data_date": "$data_date",
#                         "records_processed": "$records_processed",
#                         "duration_seconds": "$duration_seconds",
#                         "error_message": "$error_message"
#                     }},
#                     "data_dates_used": {"$addToSet": "$data_date"},
#                     "failed_datasets": {
#                         "$push": {
#                             "$cond": [
#                                 {"$eq": ["$status", "failed"]},
#                                 {"name": "$dataset_name", "error": "$error_message"},
#                                 None
#                             ]
#                         }
#                     },
#                     "first_operation": {"$min": "$start_time"},
#                     "last_operation": {"$max": "$end_time"}
#                 }},
#                 {"$project": {
#                     "date": "$_id",
#                     "total_operations": 1,
#                     "successful_operations": 1,
#                     "failed_operations": 1,
#                     "in_progress_operations": 1,
#                     "total_records_processed": 1,
#                     "total_records_inserted": 1,
#                     "total_records_deleted": 1,
#                     "success_rate": {
#                         "$cond": [
#                             {"$gt": ["$total_operations", 0]},
#                             {"$round": [
#                                 {"$multiply": [
#                                     {"$divide": ["$successful_operations", "$total_operations"]},
#                                     100
#                                 ]},
#                                 2
#                             ]},
#                             0
#                         ]
#                     },
#                     "avg_duration_seconds": {"$ifNull": [{"$round": ["$avg_duration_seconds", 2]}, 0]},
#                     "max_duration_seconds": {"$ifNull": [{"$round": ["$max_duration_seconds", 2]}, 0]},
#                     "min_duration_seconds": {"$ifNull": [{"$round": ["$min_duration_seconds", 2]}, 0]},
#                     "total_duration_hours": {
#                         "$cond": [
#                             {"$and": [{"$ne": ["$first_operation", None]}, {"$ne": ["$last_operation", None]}]},
#                             {"$round": [{
#                                 "$divide": [{
#                                     "$subtract": ["$last_operation", "$first_operation"]
#                                 }, 3600000]
#                             }, 2]},
#                             0
#                         ]
#                     },
#                     "operations": {"$slice": ["$operations", 100]},
#                     "data_dates_used": {
#                         "$filter": {
#                             "input": "$data_dates_used",
#                             "as": "date",
#                             "cond": {"$ne": ["$$date", None]}
#                         }
#                     },
#                     "failed_datasets": {
#                         "$filter": {
#                             "input": "$failed_datasets",
#                             "as": "failed",
#                             "cond": {"$ne": ["$$failed", None]}
#                         }
#                     },
#                     "generated_at": datetime.now(timezone.utc)
#                 }}
#             ]
            
#             result = list(self.operations_collection.aggregate(pipeline))
            
#             if result:
#                 summary = result[0]
#                 # Clean up the operations list
#                 if "operations" in summary:
#                     for op in summary["operations"]:
#                         if op.get("error_message") is None:
#                             op.pop("error_message", None)
                
#                 # Upsert daily summary
#                 self.daily_summary_collection.update_one(
#                     {"date": date_str},
#                     {"$set": summary},
#                     upsert=True
#                 )
                
#                 logging.info(f"[SUMMARY] Created daily summary for {date_str}: "
#                            f"{summary['successful_operations']}/{summary['total_operations']} successful")
#                 return summary
            
#             logging.warning(f"[WARNING] No operations found for date {date_str}")
#             return None
            
#         except Exception as e:
#             logging.error(f"[ERROR] Error creating daily summary: {e}")
#             return None
    
#     def get_daily_summary(self, date_str: str) -> Optional[Dict]:
#         """Get daily summary by date"""
#         return self.daily_summary_collection.find_one({"date": date_str})
    
#     def get_operation_history(self, dataset_name: Optional[str] = None, 
#                              days_back: int = 7, limit: int = 50) -> List[Dict]:
#         """Get operation history with optional filters"""
#         query = {}
        
#         # Date filter
#         cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
#         query["date"] = {"$gte": cutoff_date}
        
#         # Dataset filter
#         if dataset_name:
#             query["dataset_name"] = dataset_name
        
#         return list(self.operations_collection.find(query)
#                    .sort("start_time", pymongo.DESCENDING)
#                    .limit(limit))
    
#     def get_dataset_statistics(self, dataset_name: str, days_back: int = 30) -> Dict:
#         """Get statistics for a specific dataset"""
#         cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
        
#         try:
#             pipeline = [
#                 {"$match": {
#                     "dataset_name": dataset_name,
#                     "date": {"$gte": cutoff_date},
#                     "status": {"$in": ["success", "failed"]}
#                 }},
#                 {"$group": {
#                     "_id": "$dataset_name",
#                     "total_operations": {"$sum": 1},
#                     "successful_operations": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
#                     "failed_operations": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
#                     "total_records_processed": {"$sum": "$records_processed"},
#                     "total_records_inserted": {"$sum": "$records_inserted"},
#                     "latest_data_date": {"$max": "$data_date"},
#                     "last_scraped": {"$max": "$end_time"},
#                     "avg_duration_seconds": {"$avg": "$duration_seconds"},
#                     "success_rate": {
#                         "$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
#                     }
#                 }},
#                 {"$project": {
#                     "dataset_name": "$_id",
#                     "total_operations": 1,
#                     "successful_operations": 1,
#                     "failed_operations": 1,
#                     "total_records_processed": 1,
#                     "total_records_inserted": 1,
#                     "latest_data_date": 1,
#                     "last_scraped": 1,
#                     "avg_duration_seconds": {"$ifNull": [{"$round": ["$avg_duration_seconds", 2]}, 0]},
#                     "success_rate": {"$ifNull": [{"$round": [{"$multiply": ["$success_rate", 100]}, 2]}, 0]}
#                 }}
#             ]
            
#             result = list(self.operations_collection.aggregate(pipeline))
#             return result[0] if result else {}
#         except Exception as e:
#             logging.error(f"[ERROR] Error getting dataset statistics: {e}")
#             return {}
    
#     def cleanup_old_logs(self, days_to_keep: int = 90):
#         """Clean up logs older than specified days"""
#         try:
#             cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).strftime("%Y%m%d")
            
#             # Delete old operations
#             ops_result = self.operations_collection.delete_many({"date": {"$lt": cutoff_date}})
            
#             # Delete old summaries
#             summary_result = self.daily_summary_collection.delete_many({"date": {"$lt": cutoff_date}})
            
#             logging.info(f"[CLEANUP] Cleaned up {ops_result.deleted_count} old operations and "
#                         f"{summary_result.deleted_count} old summaries (older than {days_to_keep} days)")
#             return ops_result.deleted_count + summary_result.deleted_count
#         except Exception as e:
#             logging.error(f"[ERROR] Error cleaning up old logs: {e}")
#             return 0
    
#     def fix_missing_data_dates(self):
#         """Fix operations missing data_date by extracting from source_url"""
#         try:
#             operations = self.operations_collection.find({
#                 "data_date": {"$exists": False},
#                 "source_url": {"$exists": True, "$ne": None}
#             })
            
#             fixed_count = 0
#             for op in operations:
#                 url = op.get("source_url", "")
#                 match = re.search(r'datasets/(\d{8})/', url)
#                 if match:
#                     data_date = match.group(1)
#                     self.operations_collection.update_one(
#                         {"_id": op["_id"]},
#                         {"$set": {"data_date": data_date}}
#                     )
#                     fixed_count += 1
#                     logging.debug(f"[FIX] Fixed data_date for {op['operation_id']}: {data_date}")
            
#             if fixed_count > 0:
#                 logging.info(f"[FIX] Fixed {fixed_count} operations missing data_date")
            
#             return fixed_count
#         except Exception as e:
#             logging.error(f"[ERROR] Error fixing missing data_dates: {e}")
#             return 0

# # Initialize the scraping logger globally
# scraping_logger = ScrapingLogger(db)

# def get_current_date_string():
#     """Get current date in YYYYMMDD format"""
#     return datetime.now().strftime("%Y%m%d")

# def get_dataset_url(dataset_name, date_string=None):
#     """Generate URL with current date"""
#     if date_string is None:
#         date_string = get_current_date_string()
    
#     url = f"https://data.opensanctions.org/datasets/{date_string}/{dataset_name}/targets.nested.json"
#     return url

# def check_url_exists(url):
#     """Check if URL exists without downloading the entire file"""
#     try:
#         response = requests.head(url, timeout=10)
#         return response.status_code == 200
#     except requests.RequestException as e:
#         logging.debug(f"URL check failed: {e}")
#         return False

# def find_latest_available_date(dataset_name):
#     """Find the latest available date for a dataset by checking recent dates"""
#     current_date = datetime.now()
    
#     # Check last 7 days in case today's data isn't available yet
#     for days_back in range(7):
#         check_date = current_date - timedelta(days=days_back)
#         date_string = check_date.strftime("%Y%m%d")
#         url = get_dataset_url(dataset_name, date_string)
        
#         if check_url_exists(url):
#             logging.info(f"[OK] Found data for {dataset_name} on date: {date_string}")
#             return date_string, url
    
#     # If no recent data found, try the 'latest' endpoint as fallback
#     fallback_url = f"https://data.opensanctions.org/datasets/latest/{dataset_name}/targets.nested.json"
#     logging.warning(f"[WARNING] No recent dated data found for {dataset_name}, using fallback: {fallback_url}")
#     return None, fallback_url

# def fetch_and_store_dataset(dataset_name):
#     """Fetch and store dataset with comprehensive logging"""
#     current_date_string = get_current_date_string()
    
#     # Find the latest available data
#     data_date, url = find_latest_available_date(dataset_name)
#     if data_date:
#         logging.info(f"[SYNC] Downloading {dataset_name} from {url} (data date: {data_date})")
#     else:
#         logging.info(f"[SYNC] Downloading {dataset_name} from {url} (using latest endpoint)")
    
#     # Log operation start
#     operation_id = scraping_logger.log_operation_start(
#         dataset_name=dataset_name,
#         collection_name=dataset_name,
#         source_url=url,
#         data_date=data_date
#     )
    
#     try:
#         # Increase timeout for large datasets
#         timeout = 300
#         response = requests.get(url, timeout=timeout, stream=True)
#         response.raise_for_status()
        
#         collection = db[dataset_name]
#         # Clear existing data for this dataset
#         delete_result = collection.delete_many({})
#         records_deleted = delete_result.deleted_count
        
#         json_data = []
#         line_count = 0
#         batch_size = 1000
        
#         # Process stream to handle large files efficiently
#         for line in response.iter_lines(decode_unicode=True):
#             if line and line.strip():
#                 try:
#                     obj = json.loads(line)
#                     # Store timezone-aware UTC datetime
#                     obj["_fetched_at"] = datetime.now(timezone.utc)
#                     obj["_dataset"] = dataset_name
#                     obj["_source_url"] = url
#                     obj["_data_date"] = data_date if data_date else current_date_string
#                     json_data.append(obj)
#                     line_count += 1
                    
#                     # Batch insert to manage memory for large datasets
#                     if len(json_data) >= batch_size:
#                         collection.insert_many(json_data)
#                         logging.debug(f"[INSERT] Batch inserted {len(json_data)} records into '{dataset_name}'")
#                         json_data = []
                        
#                 except json.JSONDecodeError as e:
#                     logging.warning(f"[WARNING] JSON decode error in {dataset_name}: {str(e)}")
#                     continue

#         # Insert any remaining records
#         if json_data:
#             collection.insert_many(json_data)
#             logging.debug(f"[INSERT] Final batch inserted {len(json_data)} records into '{dataset_name}'")

#         # Create index on common fields for better query performance
#         try:
#             collection.create_index([("_dataset", pymongo.ASCENDING)])
#             collection.create_index([("_fetched_at", pymongo.DESCENDING)])
#             collection.create_index([("_data_date", pymongo.DESCENDING)])
#             indexes_created = True
#         except Exception as e:
#             logging.warning(f"[WARNING] Could not create indexes for {dataset_name}: {e}")
#             indexes_created = False

#         # Log operation success
#         scraping_logger.log_operation_success(
#             operation_id=operation_id,
#             records_processed=line_count,
#             records_inserted=line_count,
#             records_deleted=records_deleted,
#             data_date=data_date if data_date else current_date_string,
#             batch_size=batch_size,
#             indexes_created=indexes_created
#         )
        
#         logging.info(f"[OK] Successfully processed {line_count} records for '{dataset_name}' "
#                     f"(data date: {data_date if data_date else 'latest'})")
#         return True, line_count, data_date, operation_id

#     except requests.exceptions.Timeout as e:
#         error_msg = f"Timeout error processing dataset '{dataset_name}'"
#         logging.error(f"[TIMEOUT] {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg, timeout_seconds=timeout)
#         return False, 0, data_date, operation_id
#     except requests.exceptions.HTTPError as e:
#         error_msg = f"HTTP error {e.response.status_code} for dataset '{dataset_name}': {e}"
#         logging.error(f"[NETWORK] {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg, http_status=e.response.status_code)
#         return False, 0, data_date, operation_id
#     except requests.exceptions.RequestException as e:
#         error_msg = f"Network error processing dataset '{dataset_name}': {str(e)}"
#         logging.error(f"[NETWORK] {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg)
#         return False, 0, data_date, operation_id
#     except Exception as e:
#         error_msg = f"Error processing dataset '{dataset_name}': {str(e)}"
#         logging.error(f"[ERROR] {error_msg}")
#         scraping_logger.log_operation_failure(operation_id, error_msg)
#         return False, 0, data_date, operation_id

# def cleanup_stuck_operations():
#     """Find and mark operations that have been 'in_progress' for too long"""
#     try:
#         cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        
#         # Ensure cutoff_time is timezone aware
#         if cutoff_time.tzinfo is None:
#             cutoff_time = cutoff_time.replace(tzinfo=timezone.utc)
        
#         stuck_ops = db.scraping_operations.find({
#             "status": "in_progress",
#             "start_time": {"$lt": cutoff_time}
#         })
        
#         count = 0
#         for op in stuck_ops:
#             # Ensure start_time is timezone aware for calculation
#             start_time = ensure_timezone_aware(op.get("start_time"))
#             end_time = datetime.now(timezone.utc)
            
#             if start_time:
#                 duration = (end_time - start_time).total_seconds()
#             else:
#                 duration = 0
            
#             db.scraping_operations.update_one(
#                 {"_id": op["_id"]},
#                 {"$set": {
#                     "status": "abandoned",
#                     "end_time": end_time,
#                     "error_message": "Operation abandoned - likely crashed or timed out",
#                     "duration_seconds": round(duration, 2)
#                 }}
#             )
#             count += 1
#             logging.warning(f"[ALERT] Marked abandoned operation: {op['operation_id']}")
        
#         if count > 0:
#             logging.info(f"[CLEANUP] Cleaned up {count} stuck operations")
        
#         return count
#     except Exception as e:
#         logging.error(f"Error cleaning stuck operations: {e}")
#         return 0

# def main():
#     current_date = get_current_date_string()
#     total_datasets = len(DATASETS)
    
#     # Clean up stuck operations first
#     cleanup_stuck_operations()
    
#     # Fix missing data_dates in existing logs
#     scraping_logger.fix_missing_data_dates()
    
#     logging.info(f"[START] Starting OpenSanctions sync job for {total_datasets} datasets on date {current_date}")
    
#     completed = 0
#     failed = []
#     total_records = 0
#     operation_ids = []
    
#     for dataset in DATASETS:
#         try:
#             start_time = time.time()
#             success, record_count, data_date, operation_id = fetch_and_store_dataset(dataset)
#             end_time = time.time()
#             duration = end_time - start_time
            
#             if operation_id:
#                 operation_ids.append(operation_id)
            
#             if success:
#                 completed += 1
#                 total_records += record_count
#             else:
#                 failed.append(dataset)
                
#             progress = (completed / total_datasets) * 100
#             status = "[OK]" if success else "[ERROR]"
#             data_info = f"(data: {data_date})" if data_date else ""
#             logging.info(f"[PROGRESS] {status} Progress: {completed}/{total_datasets} ({progress:.1f}%) - "
#                         f"{dataset}: {record_count} records in {duration:.2f}s {data_info}")
            
#             # Small delay to be respectful to the server
#             time.sleep(1)
            
#         except Exception as e:
#             logging.error(f"[ALERT] Critical error processing {dataset}: {str(e)}")
#             failed.append(dataset)
    
#     # Create daily summary after all operations
#     try:
#         daily_summary = scraping_logger.create_daily_summary(current_date)
#     except Exception as e:
#         logging.error(f"[ERROR] Failed to create daily summary: {e}")
#         daily_summary = None
    
#     # Summary
#     logging.info(f"\n[STATS] SYNC SUMMARY for {current_date}")
#     logging.info(f"[OK] Successfully processed: {completed}/{total_datasets} datasets")
#     logging.info(f"[STATS] Total records imported: {total_records:,}")
#     if failed:
#         logging.warning(f"[ERROR] Failed datasets: {failed}")
#     else:
#         logging.info("[SUCCESS] All datasets processed successfully!")
    
#     if daily_summary:
#         logging.info(f"[SUMMARY] Success rate: {daily_summary.get('success_rate', 0)}%")
#         logging.info(f"[DATE] Data dates used: {', '.join(daily_summary.get('data_dates_used', []))}")
    
#     # Save sync metadata
#     sync_metadata = {
#         "sync_date": datetime.now(timezone.utc),
#         "data_date": current_date,
#         "total_datasets": total_datasets,
#         "successful_datasets": completed,
#         "failed_datasets": failed,
#         "total_records": total_records
#     }
    
#     try:
#         db["sync_metadata"].insert_one(sync_metadata)
#         logging.info("[SAVE] Sync metadata saved to database")
#     except Exception as e:
#         logging.error(f"[ERROR] Failed to save sync metadata: {e}")
    
#     logging.info("OpenSanctions sync job finished.\n")

# def daily_sync():
#     """Main function to run as a daily cron job"""
#     logging.info("=" * 60)
#     logging.info("[TIME] DAILY OPEN SANCTIONS SYNC STARTED")
#     logging.info("=" * 60)
    
#     # Clean up old logs (keep last 90 days) - runs daily
#     scraping_logger.cleanup_old_logs(days_to_keep=90)
    
#     main()
    
#     logging.info("=" * 60)
#     logging.info("[TIME] DAILY OPEN SANCTIONS SYNC COMPLETED")
#     logging.info("=" * 60)

# # Helper functions for manual use
# def show_scraping_history(dataset_name: Optional[str] = None, limit: int = 20):
#     """Display scraping history in a readable format"""
#     history = scraping_logger.get_operation_history(dataset_name=dataset_name, limit=limit)
    
#     if not history:
#         print("[EMPTY] No scraping history found")
#         return
    
#     print(f"\n[STATS] SCRAPING HISTORY {'for ' + dataset_name if dataset_name else ''}")
#     print("=" * 120)
#     print(f"{'Operation ID':<30} {'Dataset':<20} {'Data Date':<12} {'Start Time':<20} {'Status':<12} {'Records':<10} {'Duration':<10}")
#     print("-" * 120)
    
#     for log in history:
#         operation_id_short = log['operation_id'][-20:] if len(log['operation_id']) > 20 else log['operation_id']
#         start_time = log['start_time'].strftime('%Y-%m-%d %H:%M') if isinstance(log['start_time'], datetime) else log['start_time'][:16]
#         duration = f"{log.get('duration_seconds', 0):.1f}s" if log.get('duration_seconds') else "N/A"
#         records = log.get('records_processed', 0)
#         data_date = log.get('data_date', 'N/A')
        
#         status_text = {
#             'success': 'SUCCESS',
#             'failed': 'FAILED',
#             'in_progress': 'IN_PROGRESS',
#             'abandoned': 'ABANDONED'
#         }.get(log.get('status', ''), 'UNKNOWN')
        
#         print(f"{operation_id_short:<30} {log['dataset_name']:<20} {data_date:<12} {start_time:<20} "
#               f"{status_text:<12} {records:<10} {duration:<10}")
    
#     print("=" * 120)
#     print(f"Total operations: {len(history)}")

# def show_daily_summary(date_str: str = None):
#     """Display daily summary in readable format"""
#     if date_str is None:
#         date_str = datetime.now().strftime("%Y%m%d")
    
#     summary = scraping_logger.get_daily_summary(date_str)
    
#     if not summary:
#         print(f"[EMPTY] No daily summary found for date: {date_str}")
#         return
    
#     print(f"\n[DATE] DAILY SUMMARY for {date_str}")
#     print("=" * 70)
#     print(f"Total operations: {summary.get('total_operations', 0)}")
#     print(f"Successful: {summary.get('successful_operations', 0)}")
#     print(f"Failed: {summary.get('failed_operations', 0)}")
#     print(f"In Progress: {summary.get('in_progress_operations', 0)}")
#     print(f"Success rate: {summary.get('success_rate', 0)}%")
#     print(f"Total records processed: {summary.get('total_records_processed', 0):,}")
#     print(f"Total records inserted: {summary.get('total_records_inserted', 0):,}")
#     print(f"Average duration: {summary.get('avg_duration_seconds', 0):.1f}s")
#     print(f"Data dates used: {', '.join(summary.get('data_dates_used', []))}")
    
#     if summary.get('failed_datasets'):
#         print(f"\n[ERROR] Failed datasets:")
#         for failed in summary['failed_datasets']:
#             print(f"  - {failed.get('name', 'Unknown')}: {failed.get('error', 'No error message')}")
#     print("=" * 70)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='OpenSanctions Data Sync with Logging')
#     parser.add_argument('--run', action='store_true', help='Run the sync job')
#     parser.add_argument('--history', type=str, nargs='?', const='all',
#                        help='Show scraping history (optional: dataset name)')
#     parser.add_argument('--summary', type=str, nargs='?', const='today',
#                        help='Show daily summary (optional: date in YYYYMMDD format)')
#     parser.add_argument('--fix-dates', action='store_true',
#                        help='Fix missing data_dates in existing logs')
    
#     args = parser.parse_args()
    
#     if args.history:
#         if args.history == 'all':
#             show_scraping_history()
#         else:
#             show_scraping_history(dataset_name=args.history)
#     elif args.summary:
#         if args.summary == 'today':
#             show_daily_summary()
#         else:
#             show_daily_summary(date_str=args.summary)
#     elif args.fix_dates:
#         fixed_count = scraping_logger.fix_missing_data_dates()
#         print(f"[FIX] Fixed {fixed_count} operations with missing data dates")
#     elif args.run or len(sys.argv) == 1:  # Default to run if no arguments
#         daily_sync()
#     else:
#         print("Usage: python script.py [OPTIONS]")
#         print("\nOptions:")
#         print("  --run               Run the sync job")
#         print("  --history [NAME]    Show scraping history (optional: dataset name)")
#         print("  --summary [DATE]    Show daily summary (optional: date in YYYYMMDD)")
#         print("  --fix-dates         Fix missing data_dates in existing logs")