"""
Database backup tasks for automated backups.
"""

import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from celery import current_task
from sqlalchemy import create_engine, text

from ..core.config import settings

logger = logging.getLogger(__name__)


def run_backup(
    backup_dir: str = "./backups", retention_days: int = 30, compress: bool = True
) -> Optional[str]:
    """
    Create a PostgreSQL database backup.

    Args:
        backup_dir: Directory to store backups
        retention_days: Number of days to keep backups
        compress: Whether to compress the backup

    Returns:
        Path to the created backup file, or None if backup failed
    """
    try:
        # Ensure backup directory exists
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.sql"
        backup_file = backup_path / filename

        # Parse database URL
        db_url = settings.database_url
        if not db_url:
            logger.error("DATABASE_URL not configured")
            return None

        # Extract connection parameters
        # Format: postgresql://user:password@host:port/dbname
        parts = db_url.replace("postgresql://", "").split("@")
        if len(parts) != 2:
            logger.error(f"Invalid DATABASE_URL format: {db_url}")
            return None

        user_pass = parts[0].split(":")
        host_port_db = parts[1].split("/")

        if len(user_pass) < 2 or len(host_port_db) < 2:
            logger.error(f"Invalid DATABASE_URL format: {db_url}")
            return None

        username = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        host_port = host_port_db[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        dbname = host_port_db[1]

        # Set PGPASSWORD environment variable for pg_dump
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password

        # Build pg_dump command
        cmd = [
            "pg_dump",
            "-h",
            host,
            "-p",
            port,
            "-U",
            username,
            "-d",
            dbname,
            "--no-owner",
            "--no-acl",
            "--format=plain",
        ]

        # Add compression if requested
        if compress:
            cmd_str = " ".join(cmd) + " | gzip > " + str(backup_file) + ".gz"
            logger.info(f"Running compressed backup: {cmd_str}")
            result = subprocess.run(
                cmd_str, shell=True, env=env, capture_output=True, text=True
            )
        else:
            cmd.append("-f", str(backup_file))
            logger.info(f"Running backup: {' '.join(cmd)}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Backup failed: {result.stderr}")
            return None

        # Clean up old backups
        _cleanup_old_backups(backup_path, retention_days)

        backup_filename = f"{filename}.gz" if compress else filename
        logger.info(f"Backup created successfully: {backup_filename}")
        return str(backup_path / backup_filename)

    except Exception as e:
        logger.exception(f"Unexpected error during backup: {e}")
        return None


def _cleanup_old_backups(backup_dir: Path, retention_days: int):
    """Remove backups older than retention_days."""
    try:
        cutoff_date = datetime.utcnow().timestamp() - (retention_days * 86400)

        for backup_file in backup_dir.glob("backup_*.sql*"):
            try:
                file_mtime = backup_file.stat().st_mtime
                if file_mtime < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Removed old backup: {backup_file.name}")
            except Exception as e:
                logger.warning(f"Failed to remove old backup {backup_file}: {e}")
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")


def verify_backup(backup_file: str) -> bool:
    """
    Verify a backup file can be restored (basic check).

    Args:
        backup_file: Path to the backup file

    Returns:
        True if backup appears valid, False otherwise
    """
    try:
        # Check if file exists and is not empty
        path = Path(backup_file)
        if not path.exists() or path.stat().st_size == 0:
            return False

        # For compressed backups, check if it's valid gzip
        if backup_file.endswith(".gz"):
            import gzip

            try:
                with gzip.open(backup_file, "rt") as f:
                    # Read first few lines to verify it's a valid SQL dump
                    header = f.read(100)
                    return (
                        "-- PostgreSQL" in header
                        or "CREATE " in header
                        or "INSERT " in header
                    )
            except:
                return False
        else:
            # Plain SQL file
            with open(backup_file, "r") as f:
                header = f.read(100)
                return (
                    "-- PostgreSQL" in header
                    or "CREATE " in header
                    or "INSERT " in header
                )

    except Exception as e:
        logger.error(f"Backup verification failed: {e}")
        return False


def run_restore(backup_file: str, target_db: Optional[str] = None) -> bool:
    """
    Restore database from backup (for emergency recovery).

    Args:
        backup_file: Path to the backup file
        target_db: Target database name (defaults to current database)

    Returns:
        True if restore succeeded, False otherwise
    """
    try:
        db_url = settings.database_url
        if not db_url:
            logger.error("DATABASE_URL not configured")
            return False

        # Parse connection parameters
        parts = db_url.replace("postgresql://", "").split("@")
        if len(parts) != 2:
            logger.error(f"Invalid DATABASE_URL format: {db_url}")
            return False

        user_pass = parts[0].split(":")
        host_port_db = parts[1].split("/")

        username = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        host_port = host_port_db[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        dbname = target_db or host_port_db[1]

        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password

        # Build restore command
        if backup_file.endswith(".gz"):
            cmd_str = f"gunzip -c {backup_file} | psql -h {host} -p {port} -U {username} -d {dbname}"
            logger.info(f"Running compressed restore: {cmd_str}")
            result = subprocess.run(
                cmd_str, shell=True, env=env, capture_output=True, text=True
            )
        else:
            cmd = [
                "psql",
                "-h",
                host,
                "-p",
                port,
                "-U",
                username,
                "-d",
                dbname,
                "-f",
                backup_file,
            ]
            logger.info(f"Running restore: {' '.join(cmd)}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Restore failed: {result.stderr}")
            return False

        logger.info(f"Restore completed successfully to database: {dbname}")
        return True

    except Exception as e:
        logger.exception(f"Unexpected error during restore: {e}")
        return False
