import os
import dotenv


def configure_azure_monitor_telemetry():
    """
    Configure Azure Monitor OpenTelemetry Distro
    
    Loads environment variables and configures Azure Monitor if connection string is available.
    Returns True if configured successfully, False otherwise.
    """
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
    except ImportError:
        print("Azure Monitor OpenTelemetry package not available. Please install azure-monitor-opentelemetry")
        return False
    
    dotenv.load_dotenv()
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    if connection_string:
        configure_azure_monitor(
            connection_string=connection_string
        )
        print("Azure Monitor OpenTelemetry Distro configured")
        return True
    else:
        print("Azure Monitor OpenTelemetry Distro not configured")
        return False
