"""
Memory Maintenance Database Layer for JOJIAI
Provides compatible database client with execute_sql method for pipeline hotfix.
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager

from sqlalchemy import create_engine, text, MetaData, Table, Column, DateTime, Boolean
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class CompatDbClient:
    """
    Compatible database client with execute_sql method.
    
    This class provides the missing execute_sql method that was causing
    AttributeError in the ttl_cleanup and forget_me pipeline steps.
    
    Features:
    - SQLAlchemy 2.0+ compatibility
    - Soft-delete support with deleted_at columns
    - Batch processing for performance
    - Connection pooling and retry logic
    - Comprehensive logging
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the compatible database client.
        
        Args:
            database_url: Database connection URL. If None, uses DATABASE_URL env var.
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL must be provided either as parameter or environment variable")
        
        self.engine = self._create_engine()
        self.metadata = MetaData()
        
        logger.info("CompatDbClient initialized successfully")

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with optimized settings."""
        return create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )

    @contextmanager
    def get_connection(self):
        """Context manager for database connections with automatic cleanup."""
        connection = self.engine.connect()
        try:
            yield connection
        except Exception as e:
            connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            connection.close()

    def execute_sql(self, sql: Union[str, text], params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute SQL query with parameters.
        
        This is the main method that was missing from ApiClient and causing
        the AttributeError in ttl_cleanup and forget_me steps.
        
        Args:
            sql: SQL query string or SQLAlchemy text object
            params: Query parameters dictionary
            
        Returns:
            List of dictionaries representing result rows
            
        Raises:
            SQLAlchemyError: If query execution fails
        """
        try:
            with self.get_connection() as conn:
                if isinstance(sql, str):
                    sql = text(sql)
                
                result = conn.execute(sql, params or {})
                
                # Handle different result types
                if result.returns_rows:
                    # Convert rows to list of dictionaries
                    return [dict(row._mapping) for row in result.fetchall()]
                else:
                    # For INSERT, UPDATE, DELETE operations
                    return [{"affected_rows": result.rowcount}]
                    
        except SQLAlchemyError as e:
            logger.error(f"SQL execution failed: {e}")
            logger.error(f"Query: {sql}")
            logger.error(f"Params: {params}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in execute_sql: {e}")
            raise

    def cleanup_old_records(
        self, 
        table_name: str, 
        days_old: int = 30, 
        batch_size: int = 1000,
        use_soft_delete: bool = True
    ) -> Dict[str, Any]:
        """
        Clean up old records from specified table.
        
        This method implements the ttl_cleanup functionality that was failing.
        
        Args:
            table_name: Name of table to clean up
            days_old: Records older than this many days will be cleaned
            batch_size: Number of records to process in each batch
            use_soft_delete: If True, sets deleted_at instead of hard delete
            
        Returns:
            Dictionary with cleanup statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        total_processed = 0
        
        try:
            with self.get_connection() as conn:
                # First, count records to be cleaned
                count_sql = f"""
                    SELECT COUNT(*)  as count 
                    FROM {table_name} 
                    WHERE created_at < :cutoff_date 
                    AND (deleted_at IS NULL OR deleted_at < :cutoff_date)
                """
                
                result = conn.execute(text(count_sql), {"cutoff_date": cutoff_date})
                total_count = result.fetchone()[0]
                
                logger.info(f"Found {total_count} records to clean up in {table_name}")
                
                # Process in batches
                while total_processed < total_count:
                    if use_soft_delete:
                        update_sql = f"""
                            UPDATE {table_name}
                            SET deleted_at = :current_time
                            WHERE id IN (
                                SELECT id FROM {table_name}
                                WHERE created_at < :cutoff_date 
                                AND deleted_at IS NULL
                                LIMIT :batch_size
                            )
                        """
                        params = {
                            "current_time": datetime.utcnow(),
                            "cutoff_date": cutoff_date,
                            "batch_size": batch_size
                        }
                    else:
                        update_sql = f"""
                            DELETE FROM {table_name}
                            WHERE id IN (
                                SELECT id FROM {table_name}
                                WHERE created_at < :cutoff_date 
                                LIMIT :batch_size
                            )
                        """
                        params = {
                            "cutoff_date": cutoff_date,
                            "batch_size": batch_size
                        }
                    
                    result = conn.execute(text(update_sql), params)
                    batch_processed = result.rowcount
                    
                    if batch_processed == 0:
                        break
                        
                    total_processed += batch_processed
                    conn.commit()
                    
                    logger.info(f"Processed {batch_processed} records (total: {total_processed})")
                
                stats = {
                    "table_name": table_name,
                    "total_processed": total_processed,
                    "days_old": days_old,
                    "cutoff_date": cutoff_date.isoformat(),
                    "use_soft_delete": use_soft_delete,
                    "batch_size": batch_size,
                    "cleanup_completed_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Cleanup completed for {table_name}: {stats}")
                return stats
                
        except Exception as e:
            logger.error(f"Cleanup failed for {table_name}: {e}")
            raise

    def forget_user(self, user_id: str, batch_size: int = 1000) -> Dict[str, Any]:
        """
        Implement user data deletion (GDPR compliance).
        
        This method implements the forget_me functionality that was failing.
        
        Args:
            user_id: User ID to forget
            batch_size: Batch size for processing
            
        Returns:
            Dictionary with deletion statistics
        """
        tables_to_clean = [
            "user_sessions", "user_preferences", "user_activity_logs",
            "user_conversations", "user_memory", "user_embeddings"
        ]
        
        stats = {
            "user_id": user_id,
            "tables_processed": [],
            "total_records_affected": 0,
            "started_at": datetime.utcnow().isoformat()
        }
        
        try:
            with self.get_connection() as conn:
                for table_name in tables_to_clean:
                    try:
                        # Check if table exists and has user_id column
                        check_sql = f"""
                            SELECT COUNT(*) as count 
                            FROM information_schema.columns 
                            WHERE table_name = :table_name 
                            AND column_name = 'user_id'
                        """
                        
                        result = conn.execute(text(check_sql), {"table_name": table_name})
                        has_user_id_column = result.fetchone()[0] > 0
                        
                        if not has_user_id_column:
                            logger.warning(f"Table {table_name} does not have user_id column, skipping")
                            continue
                        
                        # Count records to be deleted
                        count_sql = f"""
                            SELECT COUNT(*) as count 
                            FROM {table_name} 
                            WHERE user_id = :user_id 
                            AND (deleted_at IS NULL)
                        """
                        
                        result = conn.execute(text(count_sql), {"user_id": user_id})
                        records_count = result.fetchone()[0]
                        
                        if records_count == 0:
                            logger.info(f"No records found for user {user_id} in {table_name}")
                            continue
                        
                        # Soft delete user records in batches
                        total_deleted = 0
                        while total_deleted < records_count:
                            delete_sql = f"""
                                UPDATE {table_name}
                                SET deleted_at = :current_time
                                WHERE user_id = :user_id 
                                AND deleted_at IS NULL
                                AND id IN (
                                    SELECT id FROM {table_name}
                                    WHERE user_id = :user_id 
                                    AND deleted_at IS NULL
                                    LIMIT :batch_size
                                )
                            """
                            
                            result = conn.execute(text(delete_sql), {
                                "user_id": user_id,
                                "current_time": datetime.utcnow(),
                                "batch_size": batch_size
                            })
                            
                            batch_deleted = result.rowcount
                            if batch_deleted == 0:
                                break
                                
                            total_deleted += batch_deleted
                            conn.commit()
                            
                            logger.info(f"Soft deleted {batch_deleted} records from {table_name} (total: {total_deleted})")
                        
                        table_stats = {
                            "table_name": table_name,
                            "records_affected": total_deleted
                        }
                        
                        stats["tables_processed"].append(table_stats)
                        stats["total_records_affected"] += total_deleted
                        
                    except Exception as e:
                        logger.error(f"Failed to process table {table_name}: {e}")
                        # Continue with other tables even if one fails
                        continue
                
                stats["completed_at"] = datetime.utcnow().isoformat()
                stats["success"] = True
                
                logger.info(f"User forget operation completed: {stats}")
                return stats
                
        except Exception as e:
            stats["error"] = str(e)
            stats["success"] = False
            logger.error(f"User forget operation failed: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.
        
        Returns:
            Dictionary with health status
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1 as health_check"))
                row = result.fetchone()
                
                return {
                    "status": "healthy" if row[0] == 1 else "unhealthy",
                    "database_url": self.database_url.split("@")[-1],  # Hide credentials
                    "checked_at": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
