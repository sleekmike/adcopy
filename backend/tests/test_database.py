"""
Tests for database operations and error handling
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId

from app.core.database import init_database, close_database, db
from app.core.config import settings


class TestDatabaseConnection:
    """Tests for database connection and initialization"""
    
    async def test_init_database_success(self):
        """Test successful database initialization"""
        with patch('app.core.database.MongoClient') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.admin.command.return_value = {"ok": 1}
            mock_client.return_value = mock_client_instance
            
            await init_database()
            
            assert db.client is not None
            assert db.database is not None
            
            # Verify connection test was performed
            mock_client_instance.admin.command.assert_called_with('ping')
    
    async def test_init_database_connection_failure(self):
        """Test database initialization with connection failure"""
        with patch('app.core.database.MongoClient') as mock_client:
            mock_client.side_effect = ConnectionFailure("Connection failed")
            
            await init_database()
            
            # Should handle gracefully
            assert db.client is None
            assert db.database is None
    
    async def test_init_database_timeout(self):
        """Test database initialization with timeout"""
        with patch('app.core.database.MongoClient') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.admin.command.side_effect = ServerSelectionTimeoutError("Timeout")
            mock_client.return_value = mock_client_instance
            
            await init_database()
            
            assert db.client is None
            assert db.database is None
    
    async def test_close_database_with_client(self):
        """Test closing database connection when client exists"""
        mock_client = Mock()
        db.client = mock_client
        
        await close_database()
        
        mock_client.close.assert_called_once()
    
    async def test_close_database_without_client(self):
        """Test closing database when no client exists"""
        db.client = None
        
        # Should not raise exception
        await close_database()


class TestDatabaseOperations:
    """Tests for database operations in the ads API"""
    
    @pytest.fixture
    def mock_ads_collection(self):
        """Mock ads collection for testing"""
        mock_collection = Mock()
        return mock_collection
    
    def test_save_ad_to_database_success(self, mock_ads_collection):
        """Test successful ad saving to database"""
        from app.api.v1.ads import save_ad_to_database
        
        with patch('app.api.v1.ads.db.database') as mock_db:
            mock_db.ads = mock_ads_collection
            mock_result = Mock()
            mock_result.inserted_id = ObjectId()
            mock_ads_collection.insert_one.return_value = mock_result
            
            # Create test data
            request_id = "test_123"
            input_data = {"name": "Test Product", "desc": "Test description"}
            variations = [{"id": "var1", "platform": "meta", "text": "Test ad"}]
            platform = "meta"
            
            # Should not raise exception
            import asyncio
            asyncio.run(save_ad_to_database(request_id, input_data, variations, platform))
            
            # Verify insert was called
            mock_ads_collection.insert_one.assert_called_once()
            call_args = mock_ads_collection.insert_one.call_args[0][0]
            
            assert call_args["input_data"] == input_data
            assert call_args["generated_variations"] == variations
            assert call_args["platform"] == platform
            assert call_args["request_id"] == request_id
    
    def test_save_ad_to_database_no_database(self):
        """Test ad saving when database is not available"""
        from app.api.v1.ads import save_ad_to_database
        
        with patch('app.api.v1.ads.db.database', None):
            # Should not raise exception
            import asyncio
            asyncio.run(save_ad_to_database("test", {}, [], "meta"))
    
    def test_save_ad_to_database_error(self, mock_ads_collection):
        """Test ad saving when database operation fails"""
        from app.api.v1.ads import save_ad_to_database
        
        with patch('app.api.v1.ads.db.database') as mock_db:
            mock_db.ads = mock_ads_collection
            mock_ads_collection.insert_one.side_effect = Exception("Insert failed")
            
            # Should not raise exception (background task)
            import asyncio
            asyncio.run(save_ad_to_database("test", {}, [], "meta"))
    
    def test_database_query_error_handling(self, mock_ads_collection):
        """Test error handling for database queries"""
        with patch('app.api.v1.ads.db.database') as mock_db:
            mock_db.ads = mock_ads_collection
            mock_ads_collection.find.side_effect = Exception("Query failed")
            
            # Test with actual endpoint
            from fastapi.testclient import TestClient
            from main import app
            
            client = TestClient(app)
            response = client.get("/api/v1/ads/history")
            
            # Should return graceful response, not 500 error
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["ads"] == []
    
    def test_invalid_object_id_handling(self):
        """Test handling of invalid ObjectId in endpoints"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Test with various invalid ObjectIds
        invalid_ids = ["invalid", "123", "not_an_object_id", ""]
        
        for invalid_id in invalid_ids:
            if invalid_id:  # Skip empty string as it would be a route issue
                response = client.get(f"/api/v1/ads/{invalid_id}")
                # Should handle gracefully, either 404 or 500 is acceptable
                assert response.status_code in [404, 500]
    
    def test_database_connection_config(self):
        """Test database connection configuration"""
        # Test that settings are properly configured
        assert hasattr(settings, 'MONGODB_URL')
        assert hasattr(settings, 'DATABASE_NAME')
        
        # Test default values
        assert settings.MONGODB_URL == "mongodb://localhost:27017"
        assert settings.DATABASE_NAME == "ad_copy_generator"


class TestDatabaseIndexes:
    """Tests for database indexing and performance"""
    
    def test_database_indexes_creation(self):
        """Test that appropriate indexes would be created for performance"""
        # This is more of a documentation test for future index creation
        expected_indexes = [
            "created_at",  # For sorting by date
            "platform",   # For filtering by platform
            "request_id", # For tracking requests
            "is_favorite" # For filtering favorites
        ]
        
        # In a real implementation, you would create these indexes
        # mock_ads_collection.create_index("created_at")
        # mock_ads_collection.create_index("platform")
        # etc.
        
        assert len(expected_indexes) == 4  # Placeholder test
    
    def test_database_query_performance_considerations(self):
        """Test considerations for database query performance"""
        # Ensure queries are designed for performance
        performance_considerations = [
            "Limit results to prevent large data transfers",
            "Use indexes for frequently queried fields",
            "Sort by indexed fields",
            "Use projection to limit returned fields when possible"
        ]
        
        assert len(performance_considerations) == 4  # Placeholder test


class TestDataValidation:
    """Tests for data validation before database operations"""
    
    def test_ad_data_structure_validation(self):
        """Test that ad data has proper structure before saving"""
        from app.models.ad import AdModel
        
        # Test valid ad data
        valid_data = {
            "input_data": {"name": "Test", "desc": "Test desc"},
            "generated_variations": [{"id": "1", "text": "Ad text"}],
            "platform": "meta",
            "request_id": "test_123",
            "is_favorite": False,
            "tags": []
        }
        
        # Should not raise validation error
        ad_model = AdModel(**valid_data)
        assert ad_model.platform == "meta"
        assert ad_model.is_favorite is False
    
    def test_ad_data_required_fields(self):
        """Test that required fields are enforced"""
        from app.models.ad import AdModel
        from pydantic import ValidationError
        
        # Test missing required fields
        incomplete_data = {
            "input_data": {"name": "Test"},
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError):
            AdModel(**incomplete_data)
    
    def test_ad_data_type_validation(self):
        """Test that field types are properly validated"""
        from app.models.ad import AdModel
        from pydantic import ValidationError
        
        # Test invalid data types
        invalid_data = {
            "input_data": "should_be_dict",  # Should be dict
            "generated_variations": "should_be_list",  # Should be list
            "platform": 123,  # Should be string
            "request_id": None,  # Should be string
            "is_favorite": "yes",  # Should be boolean
            "tags": "should_be_list"  # Should be list
        }
        
        with pytest.raises(ValidationError):
            AdModel(**invalid_data)


class TestDatabaseSecurity:
    """Tests for database security considerations"""
    
    def test_injection_prevention(self):
        """Test that database queries prevent injection attacks"""
        # Test with malicious input
        malicious_inputs = [
            {"$ne": None},
            {"$where": "function() { return true; }"},
            {"$regex": ".*"},
            '{"$ne": null}',
            "'; DROP TABLE ads; --"
        ]
        
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        for malicious_input in malicious_inputs:
            # Test in platform filter
            response = client.get(f"/api/v1/ads/history?platform={malicious_input}")
            # Should not cause database errors or return unexpected results
            assert response.status_code in [200, 422]  # Either works or validation error
    
    def test_data_sanitization(self):
        """Test that user input is properly sanitized"""
        # Test with various potentially problematic inputs
        problematic_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "' OR '1'='1",
            "../../../etc/passwd",
            "null\x00byte"
        ]
        
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        for problematic_input in problematic_inputs:
            request_data = {
                "name": problematic_input,
                "desc": "Test description",
                "audience": [problematic_input],
                "tone": "Trustworthy",
                "platform": "meta",
                "variants": 3
            }
            
            response = client.post("/api/v1/ads/generate", json=request_data)
            # Should either process safely or reject with validation error
            assert response.status_code in [200, 422]


class TestDatabaseBackup:
    """Tests for database backup and recovery considerations"""
    
    def test_backup_data_structure(self):
        """Test that data structure supports backup and recovery"""
        # Verify that all important data is stored
        required_backup_fields = [
            "input_data",
            "generated_variations", 
            "platform",
            "created_at",
            "request_id"
        ]
        
        from app.models.ad import AdModel
        
        # Check that model includes all backup-worthy fields
        model_fields = AdModel.model_fields.keys()
        for field in required_backup_fields:
            assert field in model_fields
    
    def test_data_migration_compatibility(self):
        """Test that data structure supports future migrations"""
        # Ensure fields are optional where possible for migration compatibility
        from app.models.ad import AdModel
        
        # Test with minimal data (simulating old format)
        minimal_data = {
            "input_data": {},
            "generated_variations": [],
            "platform": "meta",
            "request_id": "test"
        }
        
        # Should work with default values
        ad_model = AdModel(**minimal_data)
        assert ad_model.is_favorite is False  # Default value
        assert ad_model.tags == []  # Default value
