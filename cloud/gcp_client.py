import os
from google.cloud import bigquery, storage

class GCPClient:
    def __init__(self, project_id="oms-agentic-sentinel"):
        self.project_id = project_id
        
        # Clear any invalid credentials path to force ADC
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and not os.path.exists(cred_path):
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        try:
            self.bq_client = bigquery.Client(project=self.project_id)
            self.storage_client = storage.Client(project=self.project_id)
            print(f"🚀 GCP Connected: {self.project_id}")
        except Exception as e:
            print(f"⚠️ GCP Warning: {e}. (Running in LOCAL mode)")
            self.bq_client = None
            self.storage_client = None

    def stream_metrics_to_bq(self, dataset_id, table_id, rows):
        if not self.bq_client:
            return

        dataset_ref = self.bq_client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)

        try:
            # Auto-create dataset with explicit location
            try: 
                self.bq_client.get_dataset(dataset_ref)
            except: 
                print(f"🔨 Creating BigQuery Dataset: {dataset_id} in US...")
                new_ds = bigquery.Dataset(dataset_ref)
                new_ds.location = "US"
                self.bq_client.create_dataset(new_ds)

            # Auto-create table
            try: 
                self.bq_client.get_table(table_ref)
            except:
                print(f"🔨 Creating BigQuery Table: {table_id} in US...")
                schema = [
                    bigquery.SchemaField("timestamp", "TIMESTAMP"),
                    bigquery.SchemaField("memory_usage", "FLOAT"),
                    bigquery.SchemaField("cpu_usage", "FLOAT"),
                    bigquery.SchemaField("gc_time", "FLOAT"),
                    bigquery.SchemaField("req_rate", "FLOAT"),
                ]
                table = bigquery.Table(table_ref, schema=schema)
                self.bq_client.create_table(table) # Will inherit dataset location

            self.bq_client.insert_rows_json(table_ref, rows)
        except Exception as e:
            print(f"❌ BQ Stream Error: {e}")

    def upload_to_gcs(self, bucket_name, source_file, destination_blob):
        if not self.storage_client: return
        try:
            bucket = self.storage_client.bucket(bucket_name)
            if not bucket.exists():
                self.storage_client.create_bucket(bucket)
            blob = bucket.blob(destination_blob)
            blob.upload_from_filename(source_file)
            print(f"☁️ Uploaded {source_file} to GCS bucket {bucket_name}")
        except Exception as e:
            print(f"❌ GCS Error: {e}")
