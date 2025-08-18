"""Background tasks for async processing."""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from celery import Task
from celery.result import AsyncResult

from ..core.celery_app import celery_app
from ..core.database import SessionLocal
from ..services.refresh import refresh_all
from ..services.strategy import compute_index_and_allocations
from ..services.performance import calculate_portfolio_metrics
from ..utils.cache_utils import CacheManager
from ..models.asset import Price
from ..models.index import IndexValue, Allocation

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""

    def __call__(self, *args, **kwargs):
        """Execute task with database session."""
        db = SessionLocal()
        try:
            # Add db to kwargs for task execution
            kwargs["db"] = db
            result = self.run(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Task {self.name} failed: {e}")
            raise
        finally:
            db.close()


@celery_app.task(bind=True, base=DatabaseTask, name="refresh_market_data")
def refresh_market_data(self, mode: str = "smart", db=None) -> Dict[str, Any]:
    """
    Refresh market data in the background.

    Args:
        mode: Refresh mode (smart, full, minimal)
        db: Database session (injected by DatabaseTask)

    Returns:
        Status and statistics
    """
    try:
        start_time = datetime.utcnow()
        logger.info(f"Starting market data refresh in {mode} mode")

        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Fetching market data..."})

        # Run refresh
        refresh_all(db, smart_mode=(mode == "smart"))

        # Invalidate caches
        self.update_state(state="PROGRESS", meta={"status": "Invalidating caches..."})
        CacheManager.invalidate_market_data()
        CacheManager.invalidate_index_data()

        # Calculate metrics
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Get statistics
        price_count = db.query(Price).count()
        index_count = db.query(IndexValue).count()

        result = {
            "status": "success",
            "mode": mode,
            "duration_seconds": duration,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "statistics": {
                "total_prices": price_count,
                "total_index_values": index_count,
            },
        }

        logger.info(f"Market data refresh completed in {duration:.2f} seconds")
        return result

    except Exception as e:
        logger.error(f"Market data refresh failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery_app.task(bind=True, base=DatabaseTask, name="compute_index")
def compute_index(
    self, strategy_config: Optional[Dict] = None, db=None
) -> Dict[str, Any]:
    """
    Compute index and allocations in the background.

    Args:
        strategy_config: Optional strategy configuration override
        db: Database session (injected by DatabaseTask)

    Returns:
        Computation results
    """
    try:
        start_time = datetime.utcnow()
        logger.info("Starting index computation")

        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Computing index..."})

        # Run computation
        compute_index_and_allocations(db, config=strategy_config)

        # Calculate portfolio metrics
        self.update_state(state="PROGRESS", meta={"status": "Calculating metrics..."})
        metrics = calculate_portfolio_metrics(db)

        # Invalidate index cache
        CacheManager.invalidate_index_data()

        # Get statistics
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        index_count = db.query(IndexValue).count()
        allocation_count = db.query(Allocation).count()

        result = {
            "status": "success",
            "duration_seconds": duration,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "statistics": {
                "index_values": index_count,
                "allocations": allocation_count,
            },
            "metrics": metrics,
        }

        logger.info(f"Index computation completed in {duration:.2f} seconds")
        return result

    except Exception as e:
        logger.error(f"Index computation failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery_app.task(bind=True, base=DatabaseTask, name="generate_report")
def generate_report(
    self, report_type: str = "performance", period_days: int = 30, db=None
) -> Dict[str, Any]:
    """
    Generate various reports in the background.

    Args:
        report_type: Type of report (performance, allocation, risk)
        period_days: Period to analyze
        db: Database session (injected by DatabaseTask)

    Returns:
        Report data
    """
    try:
        start_time = datetime.utcnow()
        logger.info(f"Generating {report_type} report for {period_days} days")

        self.update_state(
            state="PROGRESS", meta={"status": f"Generating {report_type} report..."}
        )

        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        report_data = {"type": report_type, "period_days": period_days}

        if report_type == "performance":
            # Get performance metrics
            metrics = calculate_portfolio_metrics(db)

            # Get index values for period
            index_values = (
                db.query(IndexValue)
                .filter(IndexValue.date >= start_date, IndexValue.date <= end_date)
                .order_by(IndexValue.date)
                .all()
            )

            if index_values:
                start_value = index_values[0].value
                end_value = index_values[-1].value
                period_return = ((end_value / start_value) - 1) * 100

                report_data.update(
                    {
                        "period_return": period_return,
                        "start_value": start_value,
                        "end_value": end_value,
                        "metrics": metrics,
                    }
                )

        elif report_type == "allocation":
            # Get latest allocations
            latest_date = (
                db.query(Allocation.date).order_by(Allocation.date.desc()).first()
            )
            if latest_date:
                allocations = (
                    db.query(Allocation).filter(Allocation.date == latest_date[0]).all()
                )

                report_data["allocations"] = [
                    {"asset_id": a.asset_id, "weight": a.weight} for a in allocations
                ]

        elif report_type == "risk":
            # Get risk metrics
            from ..models.strategy import RiskMetrics

            latest_risk = (
                db.query(RiskMetrics).order_by(RiskMetrics.date.desc()).first()
            )

            if latest_risk:
                report_data["risk_metrics"] = {
                    "sharpe_ratio": latest_risk.sharpe_ratio,
                    "sortino_ratio": latest_risk.sortino_ratio,
                    "max_drawdown": latest_risk.max_drawdown,
                    "volatility": latest_risk.volatility,
                    "beta": latest_risk.beta_sp500,
                }

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        result = {
            "status": "success",
            "duration_seconds": duration,
            "report": report_data,
            "generated_at": end_time.isoformat(),
        }

        logger.info(f"Report generation completed in {duration:.2f} seconds")
        return result

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery_app.task(bind=True, base=DatabaseTask, name="cleanup_old_data")
def cleanup_old_data(self, days_to_keep: int = 365, db=None) -> Dict[str, Any]:
    """
    Clean up old data from the database.

    Args:
        days_to_keep: Number of days of data to retain
        db: Database session (injected by DatabaseTask)

    Returns:
        Cleanup statistics
    """
    try:
        start_time = datetime.utcnow()
        logger.info(f"Starting data cleanup, keeping {days_to_keep} days")

        self.update_state(state="PROGRESS", meta={"status": "Cleaning up old data..."})

        cutoff_date = date.today() - timedelta(days=days_to_keep)

        # Count records to delete
        old_prices = db.query(Price).filter(Price.date < cutoff_date).count()
        old_index_values = (
            db.query(IndexValue).filter(IndexValue.date < cutoff_date).count()
        )
        old_allocations = (
            db.query(Allocation).filter(Allocation.date < cutoff_date).count()
        )

        # Delete old records
        if old_prices > 0:
            db.query(Price).filter(Price.date < cutoff_date).delete()
        if old_index_values > 0:
            db.query(IndexValue).filter(IndexValue.date < cutoff_date).delete()
        if old_allocations > 0:
            db.query(Allocation).filter(Allocation.date < cutoff_date).delete()

        db.commit()

        # Invalidate caches
        CacheManager.invalidate_all()

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        result = {
            "status": "success",
            "duration_seconds": duration,
            "cutoff_date": cutoff_date.isoformat(),
            "deleted": {
                "prices": old_prices,
                "index_values": old_index_values,
                "allocations": old_allocations,
            },
            "completed_at": end_time.isoformat(),
        }

        logger.info(f"Data cleanup completed in {duration:.2f} seconds")
        return result

    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a background task.

    Args:
        task_id: Celery task ID

    Returns:
        Task status and result
    """
    try:
        result = AsyncResult(task_id, app=celery_app)

        response = {
            "task_id": task_id,
            "state": result.state,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
        }

        if result.state == "PENDING":
            response["status"] = "Task not found or not started"
        elif result.state == "PROGRESS":
            response["info"] = result.info
        elif result.state == "SUCCESS":
            response["result"] = result.result
        elif result.state == "FAILURE":
            response["error"] = str(result.info)

        return response

    except Exception as e:
        return {"task_id": task_id, "state": "ERROR", "error": str(e)}
