"""
OpenTelemetry helper module for microservices
Provides common tracing functionality with callback support for service-specific logic
"""
import os
from typing import Callable, Any, Dict, Optional, Union
from opentelemetry import trace

class OTelHelper:
    def __init__(self, service_name: Optional[str] = None):
        """
        Initialize OpenTelemetry helper
        
        Args:
            service_name: Name of the service, defaults to OTEL_SERVICE_NAME env var
        """
        self.service_name = service_name or os.getenv('OTEL_SERVICE_NAME', 'unknown-service')
        self.tracer = trace.get_tracer(__name__)
    
    def execute_with_span(
        self, 
        callback: Callable[..., Any],
        span_name: Optional[str] = None,
        context: Optional[Any] = None,
        span_attributes: Optional[Dict[str, Any]] = None,
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute a callback function within an OpenTelemetry span
        
        Args:
            callback: Function to execute within the span
            span_name: Name of the span, defaults to service name
            context: OpenTelemetry context (for parent span)
            span_attributes: Dictionary of attributes to set on the span
            *args: Arguments to pass to the callback
            **kwargs: Keyword arguments to pass to the callback
            
        Returns:
            Result of the callback function
        """
        effective_span_name = span_name or self.service_name
        
        with self.tracer.start_as_current_span(effective_span_name, context=context) as span:
            # Print trace information
            span_context = span.get_span_context()
            current_span_id = format(span_context.span_id, '016x')
            trace_id = format(span_context.trace_id, '032x')
            
            print(f"[{self.service_name}] Trace ID: {trace_id}", flush=True)
            print(f"[{self.service_name}] Span ID: {current_span_id}", flush=True)
            
            # Set span attributes
            if span_attributes:
                for key, value in span_attributes.items():
                    span.set_attribute(key, value)
            
            # Execute the callback
            return callback(*args, **kwargs)

# Global helper instance (can be overridden per service)
otel_helper = OTelHelper()
