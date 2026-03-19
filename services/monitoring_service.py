"""
Enhanced Monitoring Service - Real-time metrics and analytics.

Tracks:
- Query patterns
- Response times
- Confidence scores
- Query type distribution
- Error rates
"""
from typing import Dict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from loguru import logger


@dataclass
class QueryMetric:
    """Single query metric"""
    timestamp: str
    query_type: str
    latency_ms: float
    confidence: float
    sources_count: int
    success: bool


class MonitoringService:
    """
    Real-time monitoring and analytics service.

    Tracks all queries and provides analytics for the monitoring dashboard.
    """

    def __init__(self, max_metrics: int = 1000):
        """
        Initialize monitoring service.

        Args:
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.metrics: deque = deque(maxlen=max_metrics)
        self.query_type_counts = defaultdict(int)
        self.confidence_buckets = defaultdict(int)
        self.error_count = 0
        self.total_queries = 0

        logger.info(f"[MonitoringService] Initialized with max_metrics={max_metrics}")

    def record_query(
        self,
        query_type: str,
        latency_ms: float,
        confidence: float,
        sources_count: int,
        success: bool = True
    ):
        """
        Record a query metric.

        Args:
            query_type: Type of query
            latency_ms: Response latency in milliseconds
            confidence: Confidence score (0-1)
            sources_count: Number of sources used
            success: Whether query succeeded
        """
        metric = QueryMetric(
            timestamp=datetime.now().isoformat(),
            query_type=query_type,
            latency_ms=latency_ms,
            confidence=confidence,
            sources_count=sources_count,
            success=success
        )

        self.metrics.append(metric)
        self.total_queries += 1
        self.query_type_counts[query_type] += 1

        # Bucket confidence scores
        if confidence >= 0.9:
            self.confidence_buckets["high"] += 1
        elif confidence >= 0.7:
            self.confidence_buckets["medium"] += 1
        else:
            self.confidence_buckets["low"] += 1

        if not success:
            self.error_count += 1

    def get_real_time_stats(self) -> Dict:
        """Get current system statistics"""
        if not self.metrics:
            return self._empty_stats()

        # Calculate metrics from recent data
        recent_metrics = list(self.metrics)[-100:]  # Last 100 queries

        # Average latency
        avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)

        # Average confidence
        avg_confidence = sum(m.confidence for m in recent_metrics) / len(recent_metrics)

        # Success rate
        success_count = sum(1 for m in recent_metrics if m.success)
        success_rate = success_count / len(recent_metrics)

        # Query type distribution
        query_type_dist = dict(self.query_type_counts)

        # Confidence distribution
        confidence_dist = {
            "high": self.confidence_buckets["high"],
            "medium": self.confidence_buckets["medium"],
            "low": self.confidence_buckets["low"]
        }

        # Latency percentiles
        latencies = sorted([m.latency_ms for m in recent_metrics])
        p50 = latencies[len(latencies) // 2] if latencies else 0
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
        p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0

        return {
            "total_queries": self.total_queries,
            "avg_latency_ms": round(avg_latency, 2),
            "avg_confidence": round(avg_confidence, 3),
            "success_rate": round(success_rate, 3),
            "error_count": self.error_count,
            "emergency_count": self.query_type_counts.get("emergency", 0),
            "vector_store_size": 0,  # populated by health check if needed
            "query_type_distribution": query_type_dist,
            "confidence_distribution": confidence_dist,
            "latency_percentiles": {
                "p50": round(p50, 2),
                "p95": round(p95, 2),
                "p99": round(p99, 2)
            },
            "recent_queries_count": len(recent_metrics),
            "recent_queries": [
                {
                    "timestamp": m.timestamp,
                    "query_type": m.query_type,
                    "confidence": m.confidence,
                    "latency_ms": m.latency_ms,
                    "is_emergency": m.query_type == "emergency",
                }
                for m in list(self.metrics)[-50:]
            ],
        }

    def get_time_series_data(self, hours: int = 24) -> Dict:
        """Get time-series data for charts"""
        if not self.metrics:
            return {"timestamps": [], "query_counts": [], "avg_latencies": []}

        # Group by hour
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.metrics if datetime.fromisoformat(m.timestamp) > cutoff]

        # Group by hour
        hourly_data = defaultdict(lambda: {"count": 0, "total_latency": 0})

        for metric in recent:
            hour_key = datetime.fromisoformat(metric.timestamp).strftime("%Y-%m-%d %H:00")
            hourly_data[hour_key]["count"] += 1
            hourly_data[hour_key]["total_latency"] += metric.latency_ms

        # Sort by time
        sorted_hours = sorted(hourly_data.keys())

        timestamps = sorted_hours
        query_counts = [hourly_data[h]["count"] for h in sorted_hours]
        avg_latencies = [
            hourly_data[h]["total_latency"] / hourly_data[h]["count"]
            for h in sorted_hours
        ]

        return {
            "timestamps": timestamps,
            "query_counts": query_counts,
            "avg_latencies": avg_latencies
        }

    def get_query_type_chart_data(self) -> Dict:
        """Get query type distribution for charts"""
        return {
            "labels": list(self.query_type_counts.keys()),
            "values": list(self.query_type_counts.values())
        }

    def _empty_stats(self) -> Dict:
        """Return empty stats structure"""
        return {
            "total_queries": 0,
            "avg_latency_ms": 0,
            "avg_confidence": 0,
            "success_rate": 1.0,
            "error_count": 0,
            "emergency_count": 0,
            "vector_store_size": 0,
            "query_type_distribution": {},
            "confidence_distribution": {"high": 0, "medium": 0, "low": 0},
            "latency_percentiles": {"p50": 0, "p95": 0, "p99": 0},
            "recent_queries_count": 0,
            "recent_queries": [],
        }


# Singleton instance
monitoring_service = MonitoringService()
