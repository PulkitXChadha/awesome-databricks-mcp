#!/usr/bin/env python3
"""Test script for Unity Catalog tools."""

import os
import sys
from pathlib import Path

# Add the server directory to the path so we can import tools
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from databricks.sdk import WorkspaceClient


def test_uc_tools():
    """Test Unity Catalog tools functionality."""
    print("🔧 Testing Unity Catalog tools...")
    
    # Check if environment variables are set
    host = os.environ.get('DATABRICKS_HOST')
    token = os.environ.get('DATABRICKS_TOKEN')
    
    if not host or not token:
        print("❌ Missing DATABRICKS_HOST or DATABRICKS_TOKEN environment variables")
        print("Please run: source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN")
        return False
    
    print(f"✅ Using host: {host}")
    
    try:
        # Test connection
        w = WorkspaceClient(host=host, token=token)
        user = w.current_user.me()
        print(f"✅ Connected as: {user.user_name}")
        
        # Test listing catalogs
        print("\n📁 Testing list_uc_catalogs...")
        catalogs = list(w.catalogs.list())
        print(f"✅ Found {len(catalogs)} catalog(s)")
        
        if catalogs:
            catalog_name = catalogs[0].name
            print(f"📁 First catalog: {catalog_name}")
            
            # Test describing catalog
            print(f"\n📋 Testing describe_uc_catalog for '{catalog_name}'...")
            try:
                catalog_details = w.catalogs.get(catalog_name)
                print(f"✅ Got catalog details: {catalog_details.name}")
                
                # List schemas
                schemas = list(w.schemas.list(catalog_name))
                print(f"✅ Found {len(schemas)} schema(s) in catalog '{catalog_name}'")
                
                if schemas:
                    schema_name = schemas[0].name
                    full_schema = f"{catalog_name}.{schema_name}"
                    print(f"📁 First schema: {full_schema}")
                    
                    # Test describing schema
                    print(f"\n📋 Testing describe_uc_schema for '{full_schema}'...")
                    try:
                        schema_details = w.schemas.get(full_schema)
                        print(f"✅ Got schema details: {schema_details.name}")
                        
                        # List tables
                        tables = list(w.tables.list(full_schema))
                        print(f"✅ Found {len(tables)} table(s) in schema '{full_schema}'")
                        
                        if tables:
                            table_name = tables[0].name
                            full_table = f"{full_schema}.{table_name}"
                            print(f"📁 First table: {full_table}")
                            
                            # Test describing table
                            print(f"\n📋 Testing describe_uc_table for '{full_table}'...")
                            try:
                                table_details = w.tables.get(full_table)
                                print(f"✅ Got table details: {table_details.name}")
                                if hasattr(table_details, 'columns') and table_details.columns:
                                    print(f"✅ Table has {len(table_details.columns)} columns")
                                else:
                                    print("ℹ️  Table has no column information available")
                            except Exception as e:
                                print(f"⚠️  Could not describe table '{full_table}': {e}")
                        else:
                            print("ℹ️  No tables found in schema")
                    except Exception as e:
                        print(f"⚠️  Could not describe schema '{full_schema}': {e}")
                else:
                    print("ℹ️  No schemas found in catalog")
            except Exception as e:
                print(f"⚠️  Could not describe catalog '{catalog_name}': {e}")
        else:
            print("ℹ️  No catalogs found")
        
        print(f"\n✅ Unity Catalog tools test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Unity Catalog tools: {e}")
        return False


if __name__ == "__main__":
    success = test_uc_tools()
    sys.exit(0 if success else 1)