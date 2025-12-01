#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Enhanced API Server Integration Layer
Adds endpoints for all new modules while keeping existing functionality
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

# Import all new backend modules
try:
    import sys
    from pathlib import Path
    backend_path = Path(__file__).parent
    sys.path.insert(0, str(backend_path))
    
    from voice_engine import VoiceControlEngine
    from vision_processor import VisionProcessor
    from memory_system import MemorySystem
    from automation_engine import AutomationEngine
    from browser_agent import BrowserAgent
    from desktop_controller import DesktopController
    from file_manager import FileManager
    from avatar_controller import AvatarController
    from api_integrations import APIIntegrationManager
    
    MODULES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Backend modules not fully available: {e}")
    MODULES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

# Voice Models
class VoiceStartRequest(BaseModel):
    provider: Optional[str] = "google"  # google, whisper, sphinx

class VoiceCommandResponse(BaseModel):
    command: str
    timestamp: str

# Vision Models
class ScreenAnalysisResponse(BaseModel):
    text_length: int
    errors_detected: List[str]
    has_code: bool
    language: Optional[str]

class CameraStatusResponse(BaseModel):
    is_active: bool
    face_detected: bool
    gesture: Optional[str]

# Memory Models
class MemoryStoreRequest(BaseModel):
    content: str
    memory_type: str = "fact"  # preference, fact, conversation, skill, goal, reminder
    context: Optional[str] = None
    importance: int = 5  # 1-10

class MemoryRecallRequest(BaseModel):
    query: str
    limit: int = 10

# Workflow Models
class WorkflowCreateRequest(BaseModel):
    description: str  # Natural language

class WorkflowExecuteRequest(BaseModel):
    workflow_id: str

# Browser Models
class BrowserSearchRequest(BaseModel):
    query: str

class BrowserScrapeRequest(BaseModel):
    url: str

# Desktop Models
class DesktopCommandRequest(BaseModel):
    type: str  # window_activate, click, type, etc.
    params: Dict[str, Any]

# File Manager Models
class FileSearchRequest(BaseModel):
    query: str
    directory: Optional[str] = None
    limit: int = 50

class FileOrganizeRequest(BaseModel):
    directory: str
    method: str = "type"  # type or date

# Avatar Models
class AvatarLipSyncRequest(BaseModel):
    audio_path: str

class AvatarExpressionRequest(BaseModel):
    expression: str  # happy, sad, surprised, etc.

# ═══════════════════════════════════════════════════════════════
# INITIALIZE MODULES
# ═══════════════════════════════════════════════════════════════

def init_modules():
    """Initialize all backend modules"""
    if not MODULES_AVAILABLE:
        return {}
    
    modules = {}
    
    try:
        # Vision processor
        modules['vision'] = VisionProcessor()
        logger.info("Vision processor initialized")
    except Exception as e:
        logger.error(f"Vision init error: {e}")
    
    try:
        # Memory system
        modules['memory'] = MemorySystem()
        logger.info("Memory system initialized")
    except Exception as e:
        logger.error(f"Memory init error: {e}")
    
    try:
        # Automation engine
        modules['automation'] = AutomationEngine()
        modules['automation'].start()
        logger.info("Automation engine initialized")
    except Exception as e:
        logger.error(f"Automation init error: {e}")
    
    try:
        # Browser agent
        modules['browser'] = BrowserAgent(headless=True)
        logger.info("Browser agent initialized")
    except Exception as e:
        logger.error(f"Browser init error: {e}")
    
    try:
        # Desktop controller
        modules['desktop'] = DesktopController()
        logger.info("Desktop controller initialized")
    except Exception as e:
        logger.error(f"Desktop init error: {e}")
    
    try:
        # File manager
        modules['files'] = FileManager()
        logger.info("File manager initialized")
    except Exception as e:
        logger.error(f"File init error: {e}")
    
    try:
        # Avatar controller
        modules['avatar'] = AvatarController(fps=60)
        logger.info("Avatar controller initialized")
    except Exception as e:
        logger.error(f"Avatar init error: {e}")
    
    return modules

# Global module instances
backend_modules = init_modules()

# Voice engine (needs callback, initialized on demand)
voice_engine = None

# ═══════════════════════════════════════════════════════════════
# CREATE API ROUTER
# ═══════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/ultimate", tags=["BAIT Ultimate"])

# ═══════════════════════════════════════════════════════════════
# VOICE CONTROL ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/voice/start")
async def start_voice_control(request: VoiceStartRequest):
    """Start voice control system"""
    global voice_engine
    
    if not MODULES_AVAILABLE:
        raise HTTPException(status_code=501, detail="Modules not available")
    
    try:
        if voice_engine is None:
            # Callback for voice commands
            def on_command(text):
                logger.info(f"Voice command: {text}")
                # Could trigger other actions here
            
            from voice_engine import VoiceControlEngine
            voice_engine = VoiceControlEngine(
                stt_provider=request.provider,
                on_command=on_command
            )
        
        voice_engine.start()
        
        return {"status": "started", "provider": request.provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/stop")
async def stop_voice_control():
    """Stop voice control"""
    global voice_engine
    
    if voice_engine:
        voice_engine.stop()
        return {"status": "stopped"}
    
    return {"status": "not_running"}

# ═══════════════════════════════════════════════════════════════
# VISION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/vision/analyze-screen")
async def analyze_screen():
    """Analyze current screen content"""
    vision = backend_modules.get('vision')
    if not vision:
        raise HTTPException(status_code=501, detail="Vision module not available")
    
    try:
        context = vision.analyze_screen_context()
        
        return ScreenAnalysisResponse(
            text_length=context['text_length'],
            errors_detected=context['errors_detected'],
            has_code=context['has_code'],
            language=context.get('language')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vision/camera-status")
async def get_camera_status():
    """Get camera and presence status"""
    vision = backend_modules.get('vision')
    if not vision:
        raise HTTPException(status_code=501, detail="Vision module not available")
    
    try:
        presence = vision.check_presence()
        gesture = vision.detect_gesture() if hasattr(vision, 'detect_gesture') else None
        
        return CameraStatusResponse(
            is_active=vision.camera is not None,
            face_detected=presence,
            gesture=gesture
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# MEMORY ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/memory/store")
async def store_memory(request: MemoryStoreRequest):
    """Store new memory"""
    memory = backend_modules.get('memory')
    if not memory:
        raise HTTPException(status_code=501, detail="Memory module not available")
    
    try:
        memory_id = memory.remember(
            content=request.content,
            memory_type=request.memory_type,
            context=request.context,
            importance=request.importance
        )
        
        return {"memory_id": memory_id, "status": "stored"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/recall")
async def recall_memories(request: MemoryRecallRequest):
    """Recall memories by query"""
    memory = backend_modules.get('memory')
    if not memory:
        raise HTTPException(status_code=501, detail="Memory module not available")
    
    try:
        results = memory.recall(request.query, limit=request.limit)
        return {"memories": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memory/context/{query}")
async def get_memory_context(query: str):
    """Get memory context for AI"""
    memory = backend_modules.get('memory')
    if not memory:
        raise HTTPException(status_code=501, detail="Memory module not available")
    
    try:
        context = memory.get_context_for_query(query)
        return {"context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# AUTOMATION/WORKFLOW ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/workflow/create")
async def create_workflow(request: WorkflowCreateRequest):
    """Create workflow from natural language"""
    automation = backend_modules.get('automation')
    if not automation:
        raise HTTPException(status_code=501, detail="Automation module not available")
    
    try:
        workflow_id = automation.create_workflow(request.description)
        workflow = automation.get_workflow(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "workflow": workflow
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/list")
async def list_workflows():
    """List all workflows"""
    automation = backend_modules.get('automation')
    if not automation:
        raise HTTPException(status_code=501, detail="Automation module not available")
    
    try:
        workflows = automation.list_workflows()
        return {"workflows": workflows, "count": len(workflows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/execute")
async def execute_workflow(request: WorkflowExecuteRequest):
    """Execute workflow manually"""
    automation = backend_modules.get('automation')
    if not automation:
        raise HTTPException(status_code=501, detail="Automation module not available")
    
    try:
        success = automation.execute_workflow(request.workflow_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete workflow"""
    automation = backend_modules.get('automation')
    if not automation:
        raise HTTPException(status_code=501, detail="Automation module not available")
    
    try:
        success = automation.delete_workflow(workflow_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# BROWSER AGENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/browser/search")
async def browser_search(request: BrowserSearchRequest):
    """Search Google"""
    browser = backend_modules.get('browser')
    if not browser:
        raise HTTPException(status_code=501, detail="Browser module not available")
    
    try:
        results = browser.search_google(request.query)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/browser/scrape")
async def browser_scrape(request: BrowserScrapeRequest):
    """Scrape web page"""
    browser = backend_modules.get('browser')
    if not browser:
        raise HTTPException(status_code=501, detail="Browser module not available")
    
    try:
        data = browser.scrape_page(request.url)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# DESKTOP CONTROL ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/desktop/windows")
async def list_windows():
    """List all windows"""
    desktop = backend_modules.get('desktop')
    if not desktop:
        raise HTTPException(status_code=501, detail="Desktop module not available")
    
    try:
        windows = desktop.window_manager.list_windows()
        return {"windows": windows, "count": len(windows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/desktop/command")
async def execute_desktop_command(request: DesktopCommandRequest):
    """Execute desktop control command"""
    desktop = backend_modules.get('desktop')
    if not desktop:
        raise HTTPException(status_code=501, detail="Desktop module not available")
    
    try:
        command = {"type": request.type, **request.params}
        success = desktop.execute_command(command)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# FILE MANAGER ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/files/search")
async def search_files(request: FileSearchRequest):
    """Search files"""
    files = backend_modules.get('files')
    if not files:
        raise HTTPException(status_code=501, detail="File manager not available")
    
    try:
        results = files.search_files(
            query=request.query,
            directory=request.directory,
            limit=request.limit
        )
        return {"files": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/organize")
async def organize_directory(request: FileOrganizeRequest):
    """Organize directory"""
    files = backend_modules.get('files')
    if not files:
        raise HTTPException(status_code=501, detail="File manager not available")
    
    try:
        stats = files.organize_directory(request.directory, request.method)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/duplicates/{directory}")
async def find_duplicates(directory: str):
    """Find duplicate files"""
    files = backend_modules.get('files')
    if not files:
        raise HTTPException(status_code=501, detail="File manager not available")
    
    try:
        duplicates = files.find_and_remove_duplicates(directory, auto_remove=False)
        return {
            "duplicates": duplicates,
            "groups": len(duplicates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# AVATAR ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/avatar/lip-sync")
async def generate_lip_sync(request: AvatarLipSyncRequest):
    """Generate lip sync data from audio"""
    avatar = backend_modules.get('avatar')
    if not avatar:
        raise HTTPException(status_code=501, detail="Avatar controller not available")
    
    try:
        sync_data = avatar.generate_lip_sync(request.audio_path)
        return {
            "frames": sync_data,
            "frame_count": len(sync_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/avatar/expression")
async def set_avatar_expression(request: AvatarExpressionRequest):
    """Set avatar expression"""
    avatar = backend_modules.get('avatar')
    if not avatar:
        raise HTTPException(status_code=501, detail="Avatar controller not available")
    
    try:
        config = avatar.set_expression(request.expression)
        return {"expression": request.expression, "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/avatar/frame/{time}")
async def get_avatar_frame(time: float):
    """Get avatar frame data for specific time"""
    avatar = backend_modules.get('avatar')
    if not avatar:
        raise HTTPException(status_code=501, detail="Avatar controller not available")
    
    try:
        frame_data = avatar.get_frame_data(time)
        return frame_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@router.get("/health")
async def health_check():
    """Check status of all modules"""
    status = {
        "modules_available": MODULES_AVAILABLE,
        "active_modules": list(backend_modules.keys()),
        "voice_engine": voice_engine is not None
    }
    
    return status

logger.info("BAIT Ultimate API Routes registered")
