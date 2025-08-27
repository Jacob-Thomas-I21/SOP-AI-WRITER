"""
FDA Data Collector for Pharmaceutical SOP Training

This module collects pharmaceutical data from various FDA sources including:
- FDA Pharmaceuticals FAQ Dataset (Hugging Face)
- FDA Orange Book Database
- FDA Adverse Event Reporting System (FAERS)
- FDA Drug Labeling Dataset
- FDA 21 CFR Guidelines

All data collection follows FDA API terms of service and rate limiting.
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FDADataCollector:
    """Comprehensive FDA data collector for pharmaceutical SOP training."""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: str = "data/raw/fda"):
        """
        Initialize FDA data collector.
        
        Args:
            api_key: FDA API key for enhanced rate limits
            output_dir: Directory to save collected data
        """
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # FDA API configuration
        self.fda_base_url = "https://api.fda.gov"
        self.rate_limit_delay = 1.0  # Seconds between requests
        self.max_retries = 3
        
        # Setup requests session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Data cache for deduplication
        self.data_cache = set()
        
        logger.info(f"FDA Data Collector initialized. Output directory: {self.output_dir}")
    
    def _make_fda_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Make rate-limited request to FDA API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response data or None if failed
        """
        url = f"{self.fda_base_url}/{endpoint}"
        
        # Add API key if available
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            logger.info(f"Requesting: {endpoint}")
            time.sleep(self.rate_limit_delay)
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"FDA API request failed for {endpoint}: {e}")
            return None
    
    def collect_drug_labels(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Collect FDA drug labeling data for pharmaceutical terminology.
        
        Args:
            limit: Maximum number of records to collect
            
        Returns:
            List of drug label records
        """
        logger.info("Collecting FDA drug labeling data...")
        
        drug_labels = []
        skip = 0
        batch_size = 100  # FDA API limit
        
        while len(drug_labels) < limit:
            params = {
                'limit': min(batch_size, limit - len(drug_labels)),
                'skip': skip
            }
            
            response = self._make_fda_request('drug/label.json', params)
            
            if not response or 'results' not in response:
                logger.warning(f"No results in batch starting at {skip}")
                break
            
            batch_labels = []
            for record in response['results']:
                # Extract relevant pharmaceutical information
                label_data = {
                    'id': record.get('id', ''),
                    'set_id': record.get('set_id', ''),
                    'version': record.get('version', ''),
                    'effective_time': record.get('effective_time', ''),
                    'purpose': record.get('purpose', []),
                    'indications_and_usage': record.get('indications_and_usage', []),
                    'contraindications': record.get('contraindications', []),
                    'warnings': record.get('warnings', []),
                    'precautions': record.get('precautions', []),
                    'adverse_reactions': record.get('adverse_reactions', []),
                    'dosage_and_administration': record.get('dosage_and_administration', []),
                    'how_supplied': record.get('how_supplied', []),
                    'storage_and_handling': record.get('storage_and_handling', []),
                    'package_label_principal_display_panel': record.get('package_label_principal_display_panel', []),
                    'active_ingredient': record.get('active_ingredient', []),
                    'inactive_ingredient': record.get('inactive_ingredient', []),
                    'spl_product_data_elements': record.get('spl_product_data_elements', []),
                    'openfda': record.get('openfda', {})
                }
                
                # Create unique identifier for deduplication
                content_hash = hashlib.md5(
                    json.dumps(label_data, sort_keys=True).encode()
                ).hexdigest()
                
                if content_hash not in self.data_cache:
                    self.data_cache.add(content_hash)
                    batch_labels.append(label_data)
            
            drug_labels.extend(batch_labels)
            skip += batch_size
            
            logger.info(f"Collected {len(drug_labels)} drug labels so far...")
            
            # Check if we've reached the end
            if len(response['results']) < batch_size:
                break
        
        # Save to file
        output_file = self.output_dir / "fda_drug_labels.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(drug_labels, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collected {len(drug_labels)} FDA drug labels. Saved to {output_file}")
        return drug_labels
    
    def collect_adverse_events(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Collect FDA Adverse Event Reporting System data.
        
        Args:
            limit: Maximum number of records to collect
            
        Returns:
            List of adverse event records
        """
        logger.info("Collecting FDA adverse event data...")
        
        adverse_events = []
        skip = 0
        batch_size = 100
        
        # Focus on drug-related adverse events
        search_query = "patient.drug.drugindication:*"
        
        while len(adverse_events) < limit:
            params = {
                'search': search_query,
                'limit': min(batch_size, limit - len(adverse_events)),
                'skip': skip
            }
            
            response = self._make_fda_request('drug/event.json', params)
            
            if not response or 'results' not in response:
                logger.warning(f"No results in batch starting at {skip}")
                break
            
            batch_events = []
            for record in response['results']:
                # Extract relevant information for pharmaceutical training
                event_data = {
                    'safetyreportid': record.get('safetyreportid', ''),
                    'safetyreportversion': record.get('safetyreportversion', ''),
                    'receivedate': record.get('receivedate', ''),
                    'receivedateformat': record.get('receivedateformat', ''),
                    'transmissiondate': record.get('transmissiondate', ''),
                    'serious': record.get('serious', ''),
                    'seriousnesscongenitalanomali': record.get('seriousnesscongenitalanomali', ''),
                    'seriousnessdeath': record.get('seriousnessdeath', ''),
                    'seriousnessdisabling': record.get('seriousnessdisabling', ''),
                    'seriousnesshospitalization': record.get('seriousnesshospitalization', ''),
                    'seriousnesslifethreatening': record.get('seriousnesslifethreatening', ''),
                    'seriousnessother': record.get('seriousnessother', ''),
                    'patient': record.get('patient', {}),
                    'primarysource': record.get('primarysource', {}),
                    'reporttype': record.get('reporttype', ''),
                    'qualification': record.get('qualification', ''),
                    'literaturereference': record.get('literaturereference', ''),
                    'companynumb': record.get('companynumb', '')
                }
                
                # Create unique identifier
                content_hash = hashlib.md5(
                    f"{event_data['safetyreportid']}_{event_data['safetyreportversion']}".encode()
                ).hexdigest()
                
                if content_hash not in self.data_cache:
                    self.data_cache.add(content_hash)
                    batch_events.append(event_data)
            
            adverse_events.extend(batch_events)
            skip += batch_size
            
            logger.info(f"Collected {len(adverse_events)} adverse events so far...")
            
            if len(response['results']) < batch_size:
                break
        
        # Save to file
        output_file = self.output_dir / "fda_adverse_events.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(adverse_events, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collected {len(adverse_events)} FDA adverse events. Saved to {output_file}")
        return adverse_events
    
    def collect_drug_approvals(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Collect FDA drug approval data from Orange Book.
        
        Args:
            limit: Maximum number of records to collect
            
        Returns:
            List of drug approval records
        """
        logger.info("Collecting FDA drug approval data...")
        
        drug_approvals = []
        skip = 0
        batch_size = 100
        
        while len(drug_approvals) < limit:
            params = {
                'limit': min(batch_size, limit - len(drug_approvals)),
                'skip': skip
            }
            
            response = self._make_fda_request('drug/drugsfda.json', params)
            
            if not response or 'results' not in response:
                logger.warning(f"No results in batch starting at {skip}")
                break
            
            batch_approvals = []
            for record in response['results']:
                # Extract pharmaceutical approval information
                approval_data = {
                    'application_number': record.get('application_number', ''),
                    'sponsor_name': record.get('sponsor_name', ''),
                    'application_type': record.get('application_type', ''),
                    'submissions': record.get('submissions', []),
                    'products': record.get('products', []),
                    'openfda': record.get('openfda', {})
                }
                
                # Process submissions for regulatory information
                for submission in approval_data.get('submissions', []):
                    # Extract relevant regulatory data
                    if 'submission_type' in submission:
                        submission['regulatory_classification'] = self._classify_submission_type(
                            submission['submission_type']
                        )
                
                # Create unique identifier
                content_hash = hashlib.md5(
                    approval_data['application_number'].encode()
                ).hexdigest()
                
                if content_hash not in self.data_cache:
                    self.data_cache.add(content_hash)
                    batch_approvals.append(approval_data)
            
            drug_approvals.extend(batch_approvals)
            skip += batch_size
            
            logger.info(f"Collected {len(drug_approvals)} drug approvals so far...")
            
            if len(response['results']) < batch_size:
                break
        
        # Save to file
        output_file = self.output_dir / "fda_drug_approvals.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(drug_approvals, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collected {len(drug_approvals)} FDA drug approvals. Saved to {output_file}")
        return drug_approvals
    
    def collect_device_recalls(self, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Collect FDA medical device recall data.
        
        Args:
            limit: Maximum number of records to collect
            
        Returns:
            List of device recall records
        """
        logger.info("Collecting FDA device recall data...")
        
        device_recalls = []
        skip = 0
        batch_size = 100
        
        while len(device_recalls) < limit:
            params = {
                'limit': min(batch_size, limit - len(device_recalls)),
                'skip': skip
            }
            
            response = self._make_fda_request('device/recall.json', params)
            
            if not response or 'results' not in response:
                logger.warning(f"No results in batch starting at {skip}")
                break
            
            batch_recalls = []
            for record in response['results']:
                # Extract recall information relevant to manufacturing quality
                recall_data = {
                    'recall_number': record.get('recall_number', ''),
                    'reason_for_recall': record.get('reason_for_recall', ''),
                    'status': record.get('status', ''),
                    'distribution_pattern': record.get('distribution_pattern', ''),
                    'product_description': record.get('product_description', ''),
                    'code_info': record.get('code_info', ''),
                    'product_quantity': record.get('product_quantity', ''),
                    'recall_initiation_date': record.get('recall_initiation_date', ''),
                    'classification': record.get('classification', ''),
                    'termination_date': record.get('termination_date', ''),
                    'recall_url': record.get('recall_url', ''),
                    'openfda': record.get('openfda', {})
                }
                
                # Create unique identifier
                content_hash = hashlib.md5(
                    recall_data['recall_number'].encode()
                ).hexdigest()
                
                if content_hash not in self.data_cache:
                    self.data_cache.add(content_hash)
                    batch_recalls.append(recall_data)
            
            device_recalls.extend(batch_recalls)
            skip += batch_size
            
            logger.info(f"Collected {len(device_recalls)} device recalls so far...")
            
            if len(response['results']) < batch_size:
                break
        
        # Save to file
        output_file = self.output_dir / "fda_device_recalls.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(device_recalls, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collected {len(device_recalls)} FDA device recalls. Saved to {output_file}")
        return device_recalls
    
    def collect_huggingface_fda_data(self) -> Optional[pd.DataFrame]:
        """
        Collect FDA Pharmaceuticals FAQ dataset from Hugging Face.
        
        Returns:
            DataFrame with FAQ data or None if failed
        """
        logger.info("Collecting FDA Pharmaceuticals FAQ from Hugging Face...")
        
        try:
            from datasets import load_dataset
            
            # Load the Jaymax/FDA_Pharmaceuticals_FAQ dataset
            dataset = load_dataset("Jaymax/FDA_Pharmaceuticals_FAQ")
            
            # Convert to pandas DataFrame
            if 'train' in dataset:
                df = dataset['train'].to_pandas()
            else:
                # If no train split, use the first available split
                split_name = list(dataset.keys())[0]
                df = dataset[split_name].to_pandas()
            
            # Save to CSV and JSON formats
            csv_file = self.output_dir / "fda_pharmaceuticals_faq.csv"
            json_file = self.output_dir / "fda_pharmaceuticals_faq.json"
            
            df.to_csv(csv_file, index=False)
            df.to_json(json_file, orient='records', indent=2)
            
            logger.info(f"Collected FDA FAQ dataset: {len(df)} records")
            logger.info(f"Saved to {csv_file} and {json_file}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to collect Hugging Face FDA data: {e}")
            return None
    
    def _classify_submission_type(self, submission_type: str) -> str:
        """
        Classify FDA submission types for regulatory context.
        
        Args:
            submission_type: FDA submission type code
            
        Returns:
            Classified submission category
        """
        classification_map = {
            'ORIG': 'Original Application',
            'SUPPL': 'Supplemental Application', 
            'RESUBM': 'Resubmission',
            'AMEND': 'Amendment',
            'CORR': 'Correspondence',
            'WITHD': 'Withdrawal',
            'TYPE1': 'Type 1 - Minor Changes',
            'TYPE2': 'Type 2 - Moderate Changes', 
            'TYPE3': 'Type 3 - Major Changes',
            'PAS1': 'Prior Approval Supplement Type 1',
            'PAS2': 'Prior Approval Supplement Type 2',
            'CBE': 'Changes Being Effected',
            'CBE30': 'Changes Being Effected in 30 Days',
            'AR': 'Annual Report'
        }
        
        return classification_map.get(submission_type.upper(), 'Unknown')
    
    def collect_all_fda_data(
        self,
        drug_labels_limit: int = 1000,
        adverse_events_limit: int = 1000,
        approvals_limit: int = 1000,
        recalls_limit: int = 500
    ) -> Dict[str, Any]:
        """
        Collect all FDA datasets for pharmaceutical training.
        
        Args:
            drug_labels_limit: Max drug label records
            adverse_events_limit: Max adverse event records
            approvals_limit: Max approval records
            recalls_limit: Max recall records
            
        Returns:
            Summary of collected data
        """
        logger.info("Starting comprehensive FDA data collection...")
        
        collection_summary = {
            'start_time': datetime.utcnow().isoformat(),
            'collections': {}
        }
        
        # Collect drug labels
        try:
            drug_labels = self.collect_drug_labels(drug_labels_limit)
            collection_summary['collections']['drug_labels'] = len(drug_labels)
        except Exception as e:
            logger.error(f"Failed to collect drug labels: {e}")
            collection_summary['collections']['drug_labels'] = 0
        
        # Collect adverse events
        try:
            adverse_events = self.collect_adverse_events(adverse_events_limit)
            collection_summary['collections']['adverse_events'] = len(adverse_events)
        except Exception as e:
            logger.error(f"Failed to collect adverse events: {e}")
            collection_summary['collections']['adverse_events'] = 0
        
        # Collect drug approvals
        try:
            approvals = self.collect_drug_approvals(approvals_limit)
            collection_summary['collections']['drug_approvals'] = len(approvals)
        except Exception as e:
            logger.error(f"Failed to collect drug approvals: {e}")
            collection_summary['collections']['drug_approvals'] = 0
        
        # Collect device recalls
        try:
            recalls = self.collect_device_recalls(recalls_limit)
            collection_summary['collections']['device_recalls'] = len(recalls)
        except Exception as e:
            logger.error(f"Failed to collect device recalls: {e}")
            collection_summary['collections']['device_recalls'] = 0
        
        # Collect Hugging Face FAQ data
        try:
            faq_df = self.collect_huggingface_fda_data()
            collection_summary['collections']['fda_faq'] = len(faq_df) if faq_df is not None else 0
        except Exception as e:
            logger.error(f"Failed to collect Hugging Face FDA FAQ: {e}")
            collection_summary['collections']['fda_faq'] = 0
        
        collection_summary['end_time'] = datetime.utcnow().isoformat()
        collection_summary['total_records'] = sum(collection_summary['collections'].values())
        
        # Save collection summary
        summary_file = self.output_dir / "collection_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(collection_summary, f, indent=2)
        
        logger.info(f"FDA data collection complete. Total records: {collection_summary['total_records']}")
        logger.info(f"Summary saved to {summary_file}")
        
        return collection_summary
    
    def get_pharmaceutical_terminology(self) -> List[Dict[str, str]]:
        """
        Extract pharmaceutical terminology from collected FDA data.
        
        Returns:
            List of pharmaceutical terms and definitions
        """
        terminology = []
        
        # Load collected data files
        data_files = [
            "fda_drug_labels.json",
            "fda_adverse_events.json", 
            "fda_drug_approvals.json",
            "fda_device_recalls.json"
        ]
        
        pharmaceutical_terms = set()
        
        for file_name in data_files:
            file_path = self.output_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Extract terms based on file type
                    if 'drug_labels' in file_name:
                        for record in data:
                            # Extract from openfda fields
                            openfda = record.get('openfda', {})
                            for key, value in openfda.items():
                                if isinstance(value, list):
                                    pharmaceutical_terms.update(value)
                    
                except Exception as e:
                    logger.error(f"Error processing {file_name}: {e}")
        
        # Convert to structured format
        for term in pharmaceutical_terms:
            if term and len(term.strip()) > 2:
                terminology.append({
                    'term': term.strip(),
                    'source': 'FDA',
                    'category': 'pharmaceutical'
                })
        
        return terminology[:1000]  # Return top 1000 terms


if __name__ == "__main__":
    # Example usage
    collector = FDADataCollector(api_key=os.getenv('FDA_API_KEY'))
    
    # Collect all FDA data
    summary = collector.collect_all_fda_data(
        drug_labels_limit=500,
        adverse_events_limit=500,
        approvals_limit=500,
        recalls_limit=250
    )
    
    print(f"Collection complete: {summary}")