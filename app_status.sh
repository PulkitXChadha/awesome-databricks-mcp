#!/bin/bash

# Check the status of the Databricks App
# Usage: ./app_status.sh [--verbose]

set -e

# Parse command line arguments
VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
  VERBOSE=true
  echo "🔍 Verbose mode enabled"
fi

# Load environment variables from .env.local if it exists
if [ -f .env.local ]; then
  set -a
  source .env.local
  set +a
fi

# Validate required configuration
if [ -z "$DATABRICKS_APP_NAME" ]; then
  echo "❌ DATABRICKS_APP_NAME is not set. Please run ./setup.sh first."
  exit 1
fi

if [ -z "$DATABRICKS_AUTH_TYPE" ]; then
  echo "❌ DATABRICKS_AUTH_TYPE is not set. Please run ./setup.sh first."
  exit 1
fi

if [ "$VERBOSE" = true ] && [ -z "$DBA_SOURCE_CODE_PATH" ]; then
  echo "❌ DBA_SOURCE_CODE_PATH is not set. Please run ./setup.sh first."
  exit 1
fi

# Handle authentication based on type
echo "🔐 Authenticating with Databricks..."

if [ "$DATABRICKS_AUTH_TYPE" = "pat" ]; then
  # PAT Authentication
  if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "❌ PAT authentication requires DATABRICKS_HOST and DATABRICKS_TOKEN. Please run ./setup.sh first."
    exit 1
  fi
  
  export DATABRICKS_HOST="$DATABRICKS_HOST"
  export DATABRICKS_TOKEN="$DATABRICKS_TOKEN"
  
  # Test connection
  if ! databricks current-user me >/dev/null 2>&1; then
    echo "❌ PAT authentication failed. Please check your credentials."
    exit 1
  fi
  
elif [ "$DATABRICKS_AUTH_TYPE" = "profile" ]; then
  # Profile Authentication
  if [ -z "$DATABRICKS_CONFIG_PROFILE" ]; then
    echo "❌ Profile authentication requires DATABRICKS_CONFIG_PROFILE. Please run ./setup.sh first."
    exit 1
  fi
  
  # Test connection
  if ! databricks current-user me --profile "$DATABRICKS_CONFIG_PROFILE" >/dev/null 2>&1; then
    echo "❌ Profile authentication failed. Please check your profile configuration."
    exit 1
  fi
  
else
  echo "❌ Invalid DATABRICKS_AUTH_TYPE: $DATABRICKS_AUTH_TYPE. Must be 'pat' or 'profile'."
  exit 1
fi

echo "✅ Databricks authentication successful"
echo ""

# Function to format JSON nicely
format_json() {
  python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2))
except json.JSONDecodeError:
    print('Invalid JSON received')
    sys.exit(1)
except Exception as e:
    print(f'Error formatting JSON: {e}')
    sys.exit(1)
"
}

# Function to extract and display status info
display_status() {
  python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    
    print('📱 App Name: ${DATABRICKS_APP_NAME}')
    print('🌐 App URL: ' + data.get('url', 'Not available'))
    print('👤 Service Principal: ' + data.get('service_principal_name', 'Not available'))
    print('')
    
    # App Status
    app_status = data.get('app_status', {})
    app_state = app_status.get('state', 'Unknown')
    app_message = app_status.get('message', 'No message')
    
    if app_state == 'RUNNING':
        print('✅ App Status: RUNNING')
    elif app_state == 'UNAVAILABLE':
        print('❌ App Status: UNAVAILABLE')
    elif app_state == 'STARTING':
        print('⏳ App Status: STARTING')
    else:
        print(f'❓ App Status: {app_state}')
    
    print(f'   Message: {app_message}')
    print('')
    
    # Compute Status
    compute_status = data.get('compute_status', {})
    compute_state = compute_status.get('state', 'Unknown')
    compute_message = compute_status.get('message', 'No message')
    
    if compute_state == 'ACTIVE':
        print('✅ Compute Status: ACTIVE')
    elif compute_state == 'INACTIVE':
        print('❌ Compute Status: INACTIVE')
    elif compute_state == 'STARTING':
        print('⏳ Compute Status: STARTING')
    else:
        print(f'❓ Compute Status: {compute_state}')
    
    print(f'   Message: {compute_message}')
    print('')
    
    # Additional info
    print('ℹ️  Additional Info:')
    print(f'   Created: {data.get(\"create_time\", \"Unknown\")}')
    print(f'   Updated: {data.get(\"update_time\", \"Unknown\")}')
    print(f'   Creator: {data.get(\"creator\", \"Unknown\")}')
    print('')
    
    # Verbose mode additional details
    if '${VERBOSE}' == 'true':
        print('🔍 Verbose Details:')
        print(f'   Service Principal ID: {data.get(\"service_principal_id\", \"Not available\")}')
        print(f'   Service Principal Client ID: {data.get(\"service_principal_client_id\", \"Not available\")}')
        print(f'   OAuth2 App Client ID: {data.get(\"oauth2_app_client_id\", \"Not available\")}')
        print(f'   OAuth2 App Integration ID: {data.get(\"oauth2_app_integration_id\", \"Not available\")}')
        print(f'   Budget Policy ID: {data.get(\"effective_budget_policy_id\", \"Not available\")}')
        print(f'   Default Source Code Path: {data.get(\"default_source_code_path\", \"Not available\")}')
        print(f'   Updater: {data.get(\"updater\", \"Not available\")}')
        
        # Active deployment info
        active_deployment = data.get('active_deployment', {})
        if active_deployment:
            print(f'   Deployment ID: {active_deployment.get(\"deployment_id\", \"Not available\")}')
            print(f'   Deployment Mode: {active_deployment.get(\"mode\", \"Not available\")}')
            deployment_artifacts = active_deployment.get('deployment_artifacts', {})
            if deployment_artifacts:
                print(f'   Deployment Artifacts Path: {deployment_artifacts.get(\"source_code_path\", \"Not available\")}')
        print('')
    
except Exception as e:
    print(f'Error parsing app status: {e}')
    sys.exit(1)
"
}

# Get app status
echo "🔍 Getting app status for '$DATABRICKS_APP_NAME'..."
echo ""

if [ "$DATABRICKS_AUTH_TYPE" = "profile" ]; then
  APP_JSON=$(databricks apps get "$DATABRICKS_APP_NAME" --profile "$DATABRICKS_CONFIG_PROFILE" --output json 2>/dev/null)
else
  APP_JSON=$(databricks apps get "$DATABRICKS_APP_NAME" --output json 2>/dev/null)
fi

if [ $? -ne 0 ] || [ -z "$APP_JSON" ]; then
  echo "❌ Failed to get app status for '$DATABRICKS_APP_NAME'"
  echo "💡 Make sure the app exists by running: databricks apps list"
  exit 1
fi

# Display formatted status
echo "$APP_JSON" | display_status

# Show full JSON and workspace files if verbose
if [ "$VERBOSE" = true ]; then
  echo "📄 Full JSON Response:"
  echo "$APP_JSON" | format_json
  echo ""
  
  echo "📂 Workspace Files ($DBA_SOURCE_CODE_PATH):"
  echo ""
  
  if [ "$DATABRICKS_AUTH_TYPE" = "profile" ]; then
    WORKSPACE_LIST=$(databricks workspace list "$DBA_SOURCE_CODE_PATH" --profile "$DATABRICKS_CONFIG_PROFILE" 2>/dev/null)
  else
    WORKSPACE_LIST=$(databricks workspace list "$DBA_SOURCE_CODE_PATH" 2>/dev/null)
  fi
  
  if [ $? -ne 0 ] || [ -z "$WORKSPACE_LIST" ]; then
    echo "❌ Failed to list workspace files at '$DBA_SOURCE_CODE_PATH'"
    echo "💡 Make sure the path exists and you have access"
  else
    echo "$WORKSPACE_LIST"
  fi
  echo ""
fi

# Show helpful commands
echo "💡 Useful commands:"
if [ "$DATABRICKS_AUTH_TYPE" = "profile" ]; then
  echo "   List all apps: databricks apps list --profile $DATABRICKS_CONFIG_PROFILE"
  echo "   View logs: Visit ${DATABRICKS_APP_NAME} URL + /logz in browser"
else
  echo "   List all apps: databricks apps list"
  echo "   View logs: Visit ${DATABRICKS_APP_NAME} URL + /logz in browser"
fi
echo "   Deploy app: ./deploy.sh"
echo "   Create app: ./deploy.sh --create"