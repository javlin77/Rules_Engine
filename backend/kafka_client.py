"""
Kafka integration for async rule evaluation and event streaming
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Try to import Kafka, but make it optional
try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaError = Exception  # Fallback for type hints

logger = logging.getLogger(__name__)

class KafkaEventProducer:
    """Producer for sending events to Kafka for async rule evaluation"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.topic = os.getenv("KAFKA_EVENTS_TOPIC", "rule-events")
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Initialize Kafka producer"""
        if not KAFKA_AVAILABLE:
            logger.warning("kafka-python not installed. Kafka features disabled.")
            self.producer = None
            return
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.warning(f"Failed to connect to Kafka: {e}. Running without Kafka.")
            self.producer = None
    
    def send_event(self, event: Dict[str, Any], context: Dict[str, Any] = None, event_id: Optional[str] = None):
        """Send event to Kafka topic for async processing"""
        if not self.producer:
            logger.warning("Kafka producer not available, skipping event")
            return False
        
        try:
            message = {
                "event": event,
                "context": context or {},
                "event_id": event_id,
                "timestamp": str(datetime.utcnow())
            }
            
            key = event_id or event.get("id") or "unknown"
            future = self.producer.send(self.topic, value=message, key=key)
            
            # Wait for send to complete (optional, can be async)
            record_metadata = future.get(timeout=10)
            logger.info(f"Event sent to Kafka: topic={record_metadata.topic}, partition={record_metadata.partition}, offset={record_metadata.offset}")
            return True
        except Exception as e:
            if KAFKA_AVAILABLE and isinstance(e, KafkaError):
                logger.error(f"Failed to send event to Kafka: {e}")
            else:
                logger.error(f"Unexpected error sending to Kafka: {e}")
            return False
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.close()

# Global producer instance
_producer_instance = None

def get_kafka_producer() -> Optional[KafkaEventProducer]:
    """Get or create Kafka producer instance"""
    global _producer_instance
    if _producer_instance is None:
        _producer_instance = KafkaEventProducer()
    return _producer_instance if _producer_instance.producer else None

