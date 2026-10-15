# src/agents/__init__.py
from .video_capture import VideoCaptureAgent
from .object_detection import ObjectDetectionAgent
from .spatial_metadata import SpatialMetadataAgent
from .risk_engine import RiskEngineAgent
from .generative_ai import GenerativeAIAgent
from .audio_output import AudioOutputAgent
from .logging_agent import LoggingAgent

__all__ = [
    'VideoCaptureAgent',
    'ObjectDetectionAgent',
    'SpatialMetadataAgent',
    'RiskEngineAgent',
    'GenerativeAIAgent',
    'AudioOutputAgent',
    'LoggingAgent'
]