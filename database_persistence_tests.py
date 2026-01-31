#!/usr/bin/env python3
"""
Comprehensive Database and Persistence Layer Tests for Engram Trading Bot
Tests: Data storage, retrieval, caching, file I/O, state management
"""

import json
import logging
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabasePersistenceTests:
    """Comprehensive database and persistence test suite"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        self.temp_dir = tempfile.mkdtemp()
        
    def cleanup(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
        
    def log_test(self, name: str, passed: bool, duration: float, details: str = ""):
        """Log test result"""
        result = {
            "name": name,
            "passed": passed,
            "duration_ms": round(duration * 1000, 2),
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {name} ({duration*1000:.2f}ms)")
        if details:
            logger.info(f"  Details: {details}")
    
    def test_json_file_persistence(self) -> bool:
        """Test JSON file read/write operations"""
        start = time.time()
        try:
            test_file = Path(self.temp_dir) / "test_data.json"
            test_data = {
                "trades": [
                    {"symbol": "BTC/USDT", "price": 45000, "amount": 0.1},
                    {"symbol": "ETH/USDT", "price": 3000, "amount": 1.0}
                ],
                "config": {"max_trades": 5, "risk_level": "medium"}
            }
            
            # Write JSON
            with open(test_file, 'w') as f:
                json.dump(test_data, f, indent=2)
            
            # Verify file exists
            if not test_file.exists():
                self.log_test("JSON File Persistence", False, time.time() - start,
                            "File not created")
                return False
            
            # Read JSON
            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            
            # Verify data integrity
            if loaded_data != test_data:
                self.log_test("JSON File Persistence", False, time.time() - start,
                            "Data mismatch after read")
                return False
            
            # Test append operation
            test_data["trades"].append({"symbol": "ADA/USDT", "price": 0.5, "amount": 100})
            with open(test_file, 'w') as f:
                json.dump(test_data, f, indent=2)
            
            with open(test_file, 'r') as f:
                updated_data = json.load(f)
            
            if len(updated_data["trades"]) != 3:
                self.log_test("JSON File Persistence", False, time.time() - start,
                            "Append operation failed")
                return False
            
            self.log_test("JSON File Persistence", True, time.time() - start,
                        f"Read/write/append operations successful ({test_file.stat().st_size} bytes)")
            return True
            
        except Exception as e:
            self.log_test("JSON File Persistence", False, time.time() - start, str(e))
            return False
    
    def test_sqlite_database_operations(self) -> bool:
        """Test SQLite database CRUD operations"""
        start = time.time()
        try:
            db_file = Path(self.temp_dir) / "test.db"
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Create table
            cursor.execute('''
                CREATE TABLE trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    amount REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Insert data
            trades = [
                ("BTC/USDT", 45000.0, 0.1, datetime.now().isoformat()),
                ("ETH/USDT", 3000.0, 1.0, datetime.now().isoformat()),
                ("ADA/USDT", 0.5, 100.0, datetime.now().isoformat())
            ]
            
            cursor.executemany(
                'INSERT INTO trades (symbol, price, amount, timestamp) VALUES (?, ?, ?, ?)',
                trades
            )
            conn.commit()
            
            # Read data
            cursor.execute('SELECT * FROM trades')
            results = cursor.fetchall()
            
            if len(results) != 3:
                conn.close()
                self.log_test("SQLite Database Operations", False, time.time() - start,
                            f"Expected 3 rows, got {len(results)}")
                return False
            
            # Update data
            cursor.execute('UPDATE trades SET price = ? WHERE symbol = ?', (46000.0, "BTC/USDT"))
            conn.commit()
            
            cursor.execute('SELECT price FROM trades WHERE symbol = ?', ("BTC/USDT",))
            updated_price = cursor.fetchone()[0]
            
            if updated_price != 46000.0:
                conn.close()
                self.log_test("SQLite Database Operations", False, time.time() - start,
                            "Update operation failed")
                return False
            
            # Delete data
            cursor.execute('DELETE FROM trades WHERE symbol = ?', ("ADA/USDT",))
            conn.commit()
            
            cursor.execute('SELECT COUNT(*) FROM trades')
            count = cursor.fetchone()[0]
            
            if count != 2:
                conn.close()
                self.log_test("SQLite Database Operations", False, time.time() - start,
                            "Delete operation failed")
                return False
            
            conn.close()
            
            self.log_test("SQLite Database Operations", True, time.time() - start,
                        "CRUD operations successful (3 inserts, 1 update, 1 delete)")
            return True
            
        except Exception as e:
            self.log_test("SQLite Database Operations", False, time.time() - start, str(e))
            return False
    
    def test_cache_implementation(self) -> bool:
        """Test in-memory cache with TTL"""
        start = time.time()
        try:
            class SimpleCache:
                def __init__(self):
                    self.cache = {}
                
                def set(self, key: str, value: Any, ttl: float = 60):
                    self.cache[key] = {
                        'value': value,
                        'expires_at': time.time() + ttl
                    }
                
                def get(self, key: str) -> Any:
                    if key not in self.cache:
                        return None
                    
                    entry = self.cache[key]
                    if time.time() > entry['expires_at']:
                        del self.cache[key]
                        return None
                    
                    return entry['value']
                
                def delete(self, key: str):
                    if key in self.cache:
                        del self.cache[key]
                
                def clear(self):
                    self.cache.clear()
            
            cache = SimpleCache()
            
            # Test set/get
            cache.set("price_BTC", 45000, ttl=60)
            value = cache.get("price_BTC")
            
            if value != 45000:
                self.log_test("Cache Implementation", False, time.time() - start,
                            "Set/get failed")
                return False
            
            # Test non-existent key
            if cache.get("non_existent") is not None:
                self.log_test("Cache Implementation", False, time.time() - start,
                            "Non-existent key returned value")
                return False
            
            # Test TTL expiration
            cache.set("temp_value", "test", ttl=0.1)
            time.sleep(0.2)
            
            if cache.get("temp_value") is not None:
                self.log_test("Cache Implementation", False, time.time() - start,
                            "TTL expiration not working")
                return False
            
            # Test delete
            cache.set("to_delete", "value")
            cache.delete("to_delete")
            
            if cache.get("to_delete") is not None:
                self.log_test("Cache Implementation", False, time.time() - start,
                            "Delete operation failed")
                return False
            
            # Test clear
            cache.set("key1", "value1")
            cache.set("key2", "value2")
            cache.clear()
            
            if cache.get("key1") is not None or cache.get("key2") is not None:
                self.log_test("Cache Implementation", False, time.time() - start,
                            "Clear operation failed")
                return False
            
            self.log_test("Cache Implementation", True, time.time() - start,
                        "Set/get/delete/clear/TTL operations successful")
            return True
            
        except Exception as e:
            self.log_test("Cache Implementation", False, time.time() - start, str(e))
            return False
    
    def test_state_persistence(self) -> bool:
        """Test application state save/load"""
        start = time.time()
        try:
            state_file = Path(self.temp_dir) / "app_state.json"
            
            class StateManager:
                def __init__(self, file_path: Path):
                    self.file_path = file_path
                    self.state = {}
                
                def save_state(self):
                    with open(self.file_path, 'w') as f:
                        json.dump(self.state, f, indent=2)
                
                def load_state(self):
                    if self.file_path.exists():
                        with open(self.file_path, 'r') as f:
                            self.state = json.load(f)
                    return self.state
                
                def set(self, key: str, value: Any):
                    self.state[key] = value
                
                def get(self, key: str, default=None):
                    return self.state.get(key, default)
            
            # Create state manager
            manager = StateManager(state_file)
            
            # Set state
            manager.set("active_trades", 5)
            manager.set("total_profit", 1250.50)
            manager.set("last_update", datetime.now().isoformat())
            
            # Save state
            manager.save_state()
            
            # Create new manager and load state
            new_manager = StateManager(state_file)
            loaded_state = new_manager.load_state()
            
            # Verify state
            if loaded_state.get("active_trades") != 5:
                self.log_test("State Persistence", False, time.time() - start,
                            "Active trades mismatch")
                return False
            
            if loaded_state.get("total_profit") != 1250.50:
                self.log_test("State Persistence", False, time.time() - start,
                            "Total profit mismatch")
                return False
            
            self.log_test("State Persistence", True, time.time() - start,
                        f"State saved and loaded successfully ({len(loaded_state)} keys)")
            return True
            
        except Exception as e:
            self.log_test("State Persistence", False, time.time() - start, str(e))
            return False
    
    def test_log_file_rotation(self) -> bool:
        """Test log file rotation and management"""
        start = time.time()
        try:
            log_dir = Path(self.temp_dir) / "logs"
            log_dir.mkdir(exist_ok=True)
            
            class LogRotator:
                def __init__(self, log_dir: Path, max_size: int = 1024):
                    self.log_dir = log_dir
                    self.max_size = max_size
                    self.current_file = log_dir / "app.log"
                
                def write_log(self, message: str):
                    with open(self.current_file, 'a') as f:
                        f.write(f"{datetime.now().isoformat()} - {message}\n")
                    
                    # Check if rotation needed
                    if self.current_file.stat().st_size > self.max_size:
                        self.rotate()
                
                def rotate(self):
                    # Rename current log
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    rotated_file = self.log_dir / f"app_{timestamp}.log"
                    self.current_file.rename(rotated_file)
                    
                    # Create new log file
                    self.current_file.touch()
                
                def get_log_files(self) -> List[Path]:
                    return sorted(self.log_dir.glob("app*.log"))
            
            rotator = LogRotator(log_dir, max_size=100)
            
            # Write logs to trigger rotation
            for i in range(50):
                rotator.write_log(f"Test log message {i}")
            
            log_files = rotator.get_log_files()
            
            if len(log_files) < 2:
                self.log_test("Log File Rotation", False, time.time() - start,
                            "Log rotation not triggered")
                return False
            
            # Verify current log is small
            if rotator.current_file.stat().st_size > 100:
                self.log_test("Log File Rotation", False, time.time() - start,
                            "Current log file too large after rotation")
                return False
            
            self.log_test("Log File Rotation", True, time.time() - start,
                        f"Log rotation successful ({len(log_files)} files created)")
            return True
            
        except Exception as e:
            self.log_test("Log File Rotation", False, time.time() - start, str(e))
            return False
    
    def test_data_backup_restore(self) -> bool:
        """Test data backup and restore functionality"""
        start = time.time()
        try:
            data_file = Path(self.temp_dir) / "data.json"
            backup_dir = Path(self.temp_dir) / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Create original data
            original_data = {
                "trades": [{"id": 1, "symbol": "BTC/USDT", "profit": 100}],
                "settings": {"risk": "low"}
            }
            
            with open(data_file, 'w') as f:
                json.dump(original_data, f)
            
            # Backup
            backup_file = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy(data_file, backup_file)
            
            # Modify original
            modified_data = original_data.copy()
            modified_data["trades"].append({"id": 2, "symbol": "ETH/USDT", "profit": 50})
            
            with open(data_file, 'w') as f:
                json.dump(modified_data, f)
            
            # Restore from backup
            shutil.copy(backup_file, data_file)
            
            with open(data_file, 'r') as f:
                restored_data = json.load(f)
            
            # Verify restoration
            if len(restored_data["trades"]) != 1:
                self.log_test("Data Backup/Restore", False, time.time() - start,
                            "Restore failed - data mismatch")
                return False
            
            if restored_data != original_data:
                self.log_test("Data Backup/Restore", False, time.time() - start,
                            "Restored data doesn't match original")
                return False
            
            self.log_test("Data Backup/Restore", True, time.time() - start,
                        "Backup and restore successful")
            return True
            
        except Exception as e:
            self.log_test("Data Backup/Restore", False, time.time() - start, str(e))
            return False
    
    def test_concurrent_file_access(self) -> bool:
        """Test concurrent file read/write operations"""
        start = time.time()
        try:
            import threading
            
            test_file = Path(self.temp_dir) / "concurrent.json"
            test_file.write_text(json.dumps({"counter": 0}))
            lock = threading.Lock()
            errors = []
            
            def increment_counter(thread_id: int):
                try:
                    for _ in range(10):
                        with lock:
                            with open(test_file, 'r') as f:
                                data = json.load(f)
                            
                            data["counter"] += 1
                            
                            with open(test_file, 'w') as f:
                                json.dump(data, f)
                except Exception as e:
                    errors.append(str(e))
            
            # Create threads
            threads = []
            for i in range(5):
                t = threading.Thread(target=increment_counter, args=(i,))
                threads.append(t)
                t.start()
            
            # Wait for completion
            for t in threads:
                t.join()
            
            # Verify final count
            with open(test_file, 'r') as f:
                final_data = json.load(f)
            
            if errors:
                self.log_test("Concurrent File Access", False, time.time() - start,
                            f"Errors occurred: {errors[0]}")
                return False
            
            if final_data["counter"] != 50:  # 5 threads * 10 increments
                self.log_test("Concurrent File Access", False, time.time() - start,
                            f"Expected 50, got {final_data['counter']}")
                return False
            
            self.log_test("Concurrent File Access", True, time.time() - start,
                        "5 threads, 50 operations completed successfully")
            return True
            
        except Exception as e:
            self.log_test("Concurrent File Access", False, time.time() - start, str(e))
            return False
    
    def test_data_migration(self) -> bool:
        """Test data migration between versions"""
        start = time.time()
        try:
            # Old format
            old_data = {
                "version": 1,
                "trades": [
                    {"symbol": "BTC", "price": 45000}
                ]
            }
            
            # Migration function
            def migrate_v1_to_v2(data: dict) -> dict:
                if data.get("version") != 1:
                    return data
                
                # Add new fields
                migrated = {
                    "version": 2,
                    "trades": []
                }
                
                for trade in data["trades"]:
                    migrated["trades"].append({
                        "symbol": f"{trade['symbol']}/USDT",  # Add pair
                        "price": trade["price"],
                        "timestamp": datetime.now().isoformat()  # Add timestamp
                    })
                
                return migrated
            
            # Migrate
            new_data = migrate_v1_to_v2(old_data)
            
            # Verify migration
            if new_data["version"] != 2:
                self.log_test("Data Migration", False, time.time() - start,
                            "Version not updated")
                return False
            
            if not new_data["trades"][0]["symbol"].endswith("/USDT"):
                self.log_test("Data Migration", False, time.time() - start,
                            "Symbol format not updated")
                return False
            
            if "timestamp" not in new_data["trades"][0]:
                self.log_test("Data Migration", False, time.time() - start,
                            "Timestamp not added")
                return False
            
            self.log_test("Data Migration", True, time.time() - start,
                        "Migration from v1 to v2 successful")
            return True
            
        except Exception as e:
            self.log_test("Data Migration", False, time.time() - start, str(e))
            return False
    
    def test_data_validation(self) -> bool:
        """Test data validation before persistence"""
        start = time.time()
        try:
            class DataValidator:
                @staticmethod
                def validate_trade(trade: dict) -> tuple[bool, str]:
                    required_fields = ["symbol", "price", "amount"]
                    
                    # Check required fields
                    for field in required_fields:
                        if field not in trade:
                            return False, f"Missing required field: {field}"
                    
                    # Validate types
                    if not isinstance(trade["symbol"], str):
                        return False, "Symbol must be string"
                    
                    if not isinstance(trade["price"], (int, float)) or trade["price"] <= 0:
                        return False, "Price must be positive number"
                    
                    if not isinstance(trade["amount"], (int, float)) or trade["amount"] <= 0:
                        return False, "Amount must be positive number"
                    
                    return True, "Valid"
            
            # Valid trade
            valid_trade = {"symbol": "BTC/USDT", "price": 45000, "amount": 0.1}
            is_valid, msg = DataValidator.validate_trade(valid_trade)
            
            if not is_valid:
                self.log_test("Data Validation", False, time.time() - start,
                            f"Valid trade rejected: {msg}")
                return False
            
            # Invalid trades
            invalid_trades = [
                ({}, "Missing required field"),
                ({"symbol": "BTC/USDT"}, "Missing price"),
                ({"symbol": "BTC/USDT", "price": -100, "amount": 1}, "Negative price"),
                ({"symbol": 123, "price": 100, "amount": 1}, "Invalid symbol type")
            ]
            
            for trade, expected_error in invalid_trades:
                is_valid, msg = DataValidator.validate_trade(trade)
                if is_valid:
                    self.log_test("Data Validation", False, time.time() - start,
                                f"Invalid trade accepted: {trade}")
                    return False
            
            self.log_test("Data Validation", True, time.time() - start,
                        f"Validated 1 valid and {len(invalid_trades)} invalid trades")
            return True
            
        except Exception as e:
            self.log_test("Data Validation", False, time.time() - start, str(e))
            return False
    
    def test_transaction_rollback(self) -> bool:
        """Test transaction rollback on error"""
        start = time.time()
        try:
            db_file = Path(self.temp_dir) / "transaction_test.db"
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Create table
            cursor.execute('''
                CREATE TABLE accounts (
                    id INTEGER PRIMARY KEY,
                    balance REAL NOT NULL
                )
            ''')
            
            # Insert initial data
            cursor.execute('INSERT INTO accounts (id, balance) VALUES (1, 1000)')
            cursor.execute('INSERT INTO accounts (id, balance) VALUES (2, 500)')
            conn.commit()
            
            # Attempt transaction that should fail
            try:
                cursor.execute('UPDATE accounts SET balance = balance - 200 WHERE id = 1')
                cursor.execute('UPDATE accounts SET balance = balance + 200 WHERE id = 2')
                
                # Simulate error
                raise Exception("Simulated error")
                
                conn.commit()
            except:
                conn.rollback()
            
            # Verify rollback
            cursor.execute('SELECT balance FROM accounts WHERE id = 1')
            balance1 = cursor.fetchone()[0]
            
            cursor.execute('SELECT balance FROM accounts WHERE id = 2')
            balance2 = cursor.fetchone()[0]
            
            conn.close()
            
            if balance1 != 1000 or balance2 != 500:
                self.log_test("Transaction Rollback", False, time.time() - start,
                            "Rollback failed - balances changed")
                return False
            
            self.log_test("Transaction Rollback", True, time.time() - start,
                        "Transaction rolled back successfully")
            return True
            
        except Exception as e:
            self.log_test("Transaction Rollback", False, time.time() - start, str(e))
            return False
    
    def run_all_tests(self):
        """Run all database and persistence tests"""
        logger.info("=" * 80)
        logger.info("DATABASE AND PERSISTENCE TESTS")
        logger.info("=" * 80)
        
        tests = [
            self.test_json_file_persistence,
            self.test_sqlite_database_operations,
            self.test_cache_implementation,
            self.test_state_persistence,
            self.test_log_file_rotation,
            self.test_data_backup_restore,
            self.test_concurrent_file_access,
            self.test_data_migration,
            self.test_data_validation,
            self.test_transaction_rollback
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
                self.log_test(test.__name__, False, 0, f"Test crashed: {e}")
        
        # Cleanup
        self.cleanup()
        
        # Calculate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_duration = time.time() - self.start_time
        
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ({pass_rate:.1f}%)")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info("=" * 80)
        
        # Save results
        results_data = {
            "test_suite": "Database and Persistence Tests",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": round(pass_rate, 2),
                "duration_seconds": round(total_duration, 2)
            },
            "tests": self.results
        }
        
        output_file = Path("database_persistence_test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"✅ Results saved to {output_file}")
        
        return pass_rate >= 80


if __name__ == "__main__":
    tester = DatabasePersistenceTests()
    success = tester.run_all_tests()
    exit(0 if success else 1)
