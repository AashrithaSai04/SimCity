"""MongoDB database service for SimCity"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
import logging
import os
from config import THRESHOLDS

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self, mongo_uri: str = None):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB", "simcity")
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            self.db.command('ping')
            logger.info(f"✅ Connected to MongoDB: {self.db_name}")
            self._init_collections()
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def _init_collections(self):
        """Initialize collections with indexes"""
        collections = ["traffic", "hospitals", "supply_chain", "alerts"]
        for collection in collections:
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)
                logger.info(f"📦 Created collection: {collection}")
        
        # Create indexes
        self.db.traffic.create_index("timestamp")
        self.db.hospitals.create_index("timestamp")
        self.db.supply_chain.create_index("timestamp")
        self.db.alerts.create_index("created_at")
        self.db.alerts.create_index([("resolved", 1), ("severity", 1)])
    
    def ingest_data(self, traffic: dict, hospital: dict, supply: dict):
        """Insert data from simulator"""
        try:
            self.db.traffic.insert_one(traffic)
            self.db.hospitals.insert_one(hospital)
            self.db.supply_chain.insert_one(supply)
            
            # Check thresholds and create alerts
            self._check_thresholds()
            
            return {"status": "ok", "count": 3}
        except Exception as e:
            logger.error(f"❌ Ingest error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_thresholds(self):
        """Check data against thresholds and create alerts"""
        # Check hospital occupancy
        hospital_data = self.db.hospitals.find_one(sort=[("timestamp", -1)])
        if hospital_data and hospital_data.get("data", {}).get("bed_occupancy", 0) > THRESHOLDS["hospital_occupancy"]:
            self.db.alerts.insert_one({
                "type": "hospital_critical",
                "facility_id": hospital_data.get("metadata", {}).get("facility_id"),
                "occupancy": hospital_data.get("data", {}).get("bed_occupancy"),
                "severity": "high",
                "created_at": datetime.utcnow(),
                "resolved": False
            })
        
        # Check traffic congestion
        traffic_data = self.db.traffic.find_one(sort=[("timestamp", -1)])
        if traffic_data and traffic_data.get("data", {}).get("congestion_score", 0) > THRESHOLDS["traffic_congestion"]:
            self.db.alerts.insert_one({
                "type": "traffic_critical",
                "zone": traffic_data.get("metadata", {}).get("zone"),
                "congestion": traffic_data.get("data", {}).get("congestion_score"),
                "severity": "medium",
                "created_at": datetime.utcnow(),
                "resolved": False
            })
        
        # Check inventory
        supply_data = self.db.supply_chain.find_one(sort=[("timestamp", -1)])
        if supply_data and supply_data.get("data", {}).get("inventory_level", 100) < THRESHOLDS["supply_inventory"]:
            self.db.alerts.insert_one({
                "type": "supply_critical",
                "warehouse": supply_data.get("metadata", {}).get("warehouse"),
                "inventory": supply_data.get("data", {}).get("inventory_level"),
                "severity": "high",
                "created_at": datetime.utcnow(),
                "resolved": False
            })
    
    def get_latest_traffic(self, limit: int = 100):
        """Get latest traffic data grouped by zone"""
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
            {"$group": {
                "_id": "$metadata.zone",
                "avg_speed": {"$avg": "$data.speed"},
                "avg_congestion": {"$avg": "$data.congestion_score"},
                "incident_count": {"$sum": {"$cond": ["$data.incident_flag", 1, 0]}},
                "latest_timestamp": {"$max": "$timestamp"}
            }}
        ]
        return list(self.db.traffic.aggregate(pipeline))
    
    def get_latest_hospitals(self, limit: int = 100):
        """Get latest hospital data grouped by facility"""
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
            {"$group": {
                "_id": "$metadata.facility_id",
                "avg_occupancy": {"$avg": "$data.bed_occupancy"},
                "avg_er_wait": {"$avg": "$data.er_wait_time_minutes"},
                "critical_count": {"$sum": {"$cond": ["$data.critical_status", 1, 0]}},
                "latest_timestamp": {"$max": "$timestamp"}
            }}
        ]
        return list(self.db.hospitals.aggregate(pipeline))
    
    def get_latest_supply(self, limit: int = 100):
        """Get latest supply chain data grouped by warehouse"""
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
            {"$group": {
                "_id": "$metadata.warehouse",
                "avg_inventory": {"$avg": "$data.inventory_level"},
                "avg_eta": {"$avg": "$data.delivery_eta_hours"},
                "critical_count": {"$sum": {"$cond": ["$data.stock_critical", 1, 0]}},
                "latest_timestamp": {"$max": "$timestamp"}
            }}
        ]
        return list(self.db.supply_chain.aggregate(pipeline))
    
    def get_alerts(self, limit: int = 50):
        """Get recent alerts"""
        alerts = list(self.db.alerts.find().sort("created_at", -1).limit(limit))
        for alert in alerts:
            alert["_id"] = str(alert["_id"])
            alert["created_at"] = alert["created_at"].isoformat()
        return alerts
    
    def get_active_alerts(self):
        """Get unresolved alerts"""
        alerts = list(self.db.alerts.find({"resolved": False}).sort("created_at", -1))
        for alert in alerts:
            alert["_id"] = str(alert["_id"])
            alert["created_at"] = alert["created_at"].isoformat()
        return alerts
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")