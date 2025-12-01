#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Automation & Workflow Engine
- Natural language workflow creation
- Time-based scheduling
- Event-based triggers
- Action execution
- Workflow persistence
"""

import os
import json
import logging
import threading
import schedule
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# WORKFLOW PARSER
# ═══════════════════════════════════════════════════════════════

class WorkflowParser:
    """
    Parses natural language into workflow definitions
    """
    
    # Time patterns
    TIME_PATTERNS = {
        r'every day at (\d{1,2}):?(\d{2})?\s*(am|pm)?': 'daily',
        r'every morning at (\d{1,2})': 'daily_morning',
        r'every (\d+) (minute|hour)s?': 'interval',
        r'at (\d{1,2}):?(\d{2})?\s*(am|pm)?': 'once',
        r'when i say ["\'](.+?)["\']': 'voice_command',
        r'when (.+?) opens?': 'app_open',
        r'when battery is below (\d+)': 'battery_low'
    }
    
    # Action patterns
    ACTION_PATTERNS = {
        r'open (.+)': 'open_app',
        r'close (.+)': 'close_app',
        r'go to (.+)': 'open_url',
        r'play (.+)': 'play_music',
        r'send email to (.+)': 'send_email',
        r'create file (.+)': 'create_file',
        r'run command (.+)': 'run_command',
        r'search (.+) for (.+)': 'web_search'
    }
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language workflow description
        
        Args:
            text: Natural language workflow
            
        Returns:
            Workflow definition dict
        """
        workflow = {
            'name': self._extract_name(text),
            'triggers': self._extract_triggers(text),
            'actions': self._extract_actions(text),
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        
        return workflow
    
    def _extract_name(self, text: str) -> str:
        """Extract or generate workflow name"""
        # Use first line or generate from content
        first_line = text.split('.')[0].strip()
        if len(first_line) < 50:
            return first_line
        return f"Workflow {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _extract_triggers(self, text: str) -> List[Dict[str, Any]]:
        """Extract triggers from text"""
        triggers = []
        text_lower = text.lower()
        
        for pattern, trigger_type in self.TIME_PATTERNS.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                if trigger_type == 'daily':
                    hour = int(match.group(1))
                    minute = int(match.group(2) or 0)
                    am_pm = match.group(3)
                    
                    if am_pm == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                    
                    triggers.append({
                        'type': 'time',
                        'schedule': 'daily',
                        'hour': hour,
                        'minute': minute
                    })
                
                elif trigger_type == 'interval':
                    number = int(match.group(1))
                    unit = match.group(2)
                    triggers.append({
                        'type': 'interval',
                        'value': number,
                        'unit': unit
                    })
                
                elif trigger_type == 'voice_command':
                    command = match.group(1)
                    triggers.append({
                        'type': 'voice',
                        'command': command
                    })
                
                elif trigger_type == 'app_open':
                    app = match.group(1)
                    triggers.append({
                        'type': 'app_event',
                        'app': app,
                        'event': 'open'
                    })
                
                elif trigger_type == 'battery_low':
                    threshold = int(match.group(1))
                    triggers.append({
                        'type': 'system',
                        'condition': 'battery_low',
                        'threshold': threshold
                    })
        
        return triggers if triggers else [{'type': 'manual'}]
    
    def _extract_actions(self, text: str) -> List[Dict[str, Any]]:
        """Extract actions from text"""
        actions = []
        text_lower = text.lower()
        
        # Split by common separators
        action_lines = re.split(r'[,;]|\s+then\s+|\s+and\s+', text_lower)
        
        for line in action_lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern, action_type in self.ACTION_PATTERNS.items():
                match = re.search(pattern, line)
                if match:
                    if action_type == 'open_app':
                        actions.append({
                            'type': 'open_app',
                            'name': match.group(1).strip()
                        })
                    elif action_type == 'open_url':
                        actions.append({
                            'type': 'open_url',
                            'url': match.group(1).strip()
                        })
                    elif action_type == 'web_search':
                        actions.append({
                            'type': 'web_search',
                            'platform': match.group(1).strip(),
                            'query': match.group(2).strip()
                        })
                    # Add more action types as needed
        
        return actions

# ═══════════════════════════════════════════════════════════════
# WORKFLOW SCHEDULER
# ═══════════════════════════════════════════════════════════════

class WorkflowScheduler:
    """
    Schedules and executes workflows based on triggers
    """
    
    def __init__(self, action_executor: 'ActionExecutor'):
        """
        Initialize scheduler
        
        Args:
            action_executor: ActionExecutor instance
        """
        self.action_executor = action_executor
        self.workflows = {}
        self.is_running = False
        self.scheduler_thread = None
        
        logger.info("Workflow Scheduler initialized")
    
    def add_workflow(self, workflow_id: str, workflow: Dict[str, Any]):
        """Add workflow to scheduler"""
        self.workflows[workflow_id] = workflow
        
        if workflow.get('enabled', True):
            self._schedule_workflow(workflow_id, workflow)
        
        logger.info(f"Added workflow: {workflow['name']}")
    
    def _schedule_workflow(self, workflow_id: str, workflow: Dict[str, Any]):
        """Schedule workflow based on triggers"""
        for trigger in workflow.get('triggers', []):
            trigger_type = trigger.get('type')
            
            if trigger_type == 'time':
                # Time-based scheduling
                hour = trigger.get('hour', 0)
                minute = trigger.get('minute', 0)
                time_str = f"{hour:02d}:{minute:02d}"
                
                schedule.every().day.at(time_str).do(
                    self._execute_workflow,
                    workflow_id=workflow_id
                ).tag(workflow_id)
                
                logger.info(f"Scheduled {workflow['name']} for {time_str} daily")
            
            elif trigger_type == 'interval':
                # Interval-based scheduling
                value = trigger.get('value', 1)
                unit = trigger.get('unit', 'minute')
                
                if unit == 'minute':
                    schedule.every(value).minutes.do(
                        self._execute_workflow,
                        workflow_id=workflow_id
                    ).tag(workflow_id)
                elif unit == 'hour':
                    schedule.every(value).hours.do(
                        self._execute_workflow, 
                        workflow_id=workflow_id
                    ).tag(workflow_id)
                
                logger.info(f"Scheduled {workflow['name']} every {value} {unit}(s)")
    
    def _execute_workflow(self, workflow_id: str):
        """Execute workflow actions"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return
        
        logger.info(f"Executing workflow: {workflow['name']}")
        
        for action in workflow.get('actions', []):
            try:
                self.action_executor.execute(action)
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
    
    def remove_workflow(self, workflow_id: str):
        """Remove workflow from scheduler"""
        if workflow_id in self.workflows:
            # Clear scheduled jobs
            schedule.clear(workflow_id)
            del self.workflows[workflow_id]
            logger.info(f"Removed workflow: {workflow_id}")
    
    def start(self):
        """Start scheduler in background thread"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        self.is_running = False
        logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """Background scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)

# ═══════════════════════════════════════════════════════════════
# ACTION EXECUTOR
# ═══════════════════════════════════════════════════════════════

class ActionExecutor:
    """
    Executes workflow actions
    """
    
    def __init__(self):
        """Initialize action executor"""
        self.action_handlers = self._register_handlers()
        logger.info("Action Executor initialized")
    
    def _register_handlers(self) -> Dict[str, Callable]:
        """Register action handlers"""
        return {
            'open_app': self._open_app,
            'close_app': self._close_app,
            'open_url': self._open_url,
            'run_command': self._run_command,
            'create_file': self._create_file,
            'web_search': self._web_search,
            'send_notification': self._send_notification
        }
    
    def execute(self, action: Dict[str, Any]) -> bool:
        """
        Execute single action
        
        Args:
            action: Action definition
            
        Returns:
            True if successful
        """
        action_type = action.get('type')
        handler = self.action_handlers.get(action_type)
        
        if not handler:
            logger.error(f"Unknown action type: {action_type}")
            return False
        
        try:
            handler(action)
            logger.info(f"Executed action: {action_type}")
            return True
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return False
    
    def _open_app(self, action: Dict[str, Any]):
        """Open application"""
        app_name = action.get('name', '')
        os.startfile(app_name)
    
    def _close_app(self, action: Dict[str, Any]):
        """Close application"""
        app_name = action.get('name', '')
        os.system(f"taskkill /IM {app_name}.exe /F")
    
    def _open_url(self, action: Dict[str, Any]):
        """Open URL in browser"""
        import webbrowser
        url = action.get('url', '')
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        webbrowser.open(url)
    
    def _run_command(self, action: Dict[str, Any]):
        """Run shell command"""
        command = action.get('command', '')
        os.system(command)
    
    def _create_file(self, action: Dict[str, Any]):
        """Create file"""
        filepath = action.get('path', '')
        content = action.get('content', '')
        with open(filepath, 'w') as f:
            f.write(content)
    
    def _web_search(self, action: Dict[str, Any]):
        """Perform web search"""
        import webbrowser
        platform = action.get('platform', 'google')
        query = action.get('query', '')
        
        if platform.lower() == 'google':
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        elif platform.lower() == 'youtube':
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        else:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        webbrowser.open(url)
    
    def _send_notification(self, action: Dict[str, Any]):
        """Send system notification"""
        # Platform-specific notification
        pass

# ═══════════════════════════════════════════════════════════════
# AUTOMATION ENGINE (Main Class)
# ═══════════════════════════════════════════════════════════════

class AutomationEngine:
    """
    Main automation and workflow engine
    """
    
    def __init__(self, storage_path: str = "workflows.json"):
        """
        Initialize automation engine
        
        Args:
            storage_path: Path to workflow storage file
        """
        self.storage_path = storage_path
        self.parser = WorkflowParser()
        self.action_executor = ActionExecutor()
        self.scheduler = WorkflowScheduler(self.action_executor)
        
        # Load existing workflows
        self.workflows = self._load_workflows()
        
        # Add to scheduler
        for wf_id, wf in self.workflows.items():
            if wf.get('enabled', True):
                self.scheduler.add_workflow(wf_id, wf)
        
        logger.info("Automation Engine initialized")
    
    def _load_workflows(self) -> Dict[str, Any]:
        """Load workflows from storage"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_workflows(self):
        """Save workflows to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.workflows, f, indent=2)
        logger.info("Workflows saved")
    
    def create_workflow(self, text: str) -> str:
        """
        Create workflow from natural language
        
        Args:
            text: Natural language workflow description
            
        Returns:
            Workflow ID
        """
        workflow = self.parser.parse(text)
        workflow_id = f"wf_{int(datetime.now().timestamp())}"
        
        self.workflows[workflow_id] = workflow
        self.scheduler.add_workflow(workflow_id, workflow)
        self._save_workflows()
        
        logger.info(f"Created workflow: {workflow['name']}")
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows"""
        return [
            {'id': wf_id, **wf}
            for wf_id, wf in self.workflows.items()
        ]
    
    def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow"""
        if workflow_id not in self.workflows:
            return False
        
        self.workflows[workflow_id].update(updates)
        self._save_workflows()
        
        # Reschedule if enabled status changed
        if 'enabled' in updates:
            self.scheduler.remove_workflow(workflow_id)
            if updates['enabled']:
                self.scheduler.add_workflow(workflow_id, self.workflows[workflow_id])
        
        return True
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow"""
        if workflow_id not in self.workflows:
            return False
        
        self.scheduler.remove_workflow(workflow_id)
        del self.workflows[workflow_id]
        self._save_workflows()
        
        logger.info(f"Deleted workflow: {workflow_id}")
        return True
    
    def execute_workflow(self, workflow_id: str) -> bool:
        """Manually execute workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        
        for action in workflow.get('actions', []):
            self.action_executor.execute(action)
        
        return True
    
    def start(self):
        """Start automation engine"""
        self.scheduler.start()
        logger.info("Automation Engine started")
    
    def stop(self):
        """Stop automation engine"""
        self.scheduler.stop()
        logger.info("Automation Engine stopped")

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT Automation Engine - Test Mode")
    print("=" * 60)
    
    engine = AutomationEngine()
    
    # Create test workflow
    print("\n📝 Creating workflow...")
    workflow_text = "Every day at 9:00 am, open chrome and go to gmail.com"
    workflow_id = engine.create_workflow(workflow_text)
    print(f"  Created: {workflow_id}")
    
    # List workflows
    print("\n📋 All workflows:")
    for wf in engine.list_workflows():
        print(f"  - {wf['name']} (ID: {wf['id']}, Enabled: {wf['enabled']})")
    
    # Show workflow details
    workflow = engine.get_workflow(workflow_id)
    print(f"\n📄 Workflow details:")
    print(f"  Triggers: {workflow['triggers']}")
    print(f"  Actions: {workflow['actions']}")
    
    # Start engine
    print("\n▶️  Starting automation engine...")
    engine.start()
    
    print("\nEngine running. Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping...")
        engine.stop()
        print("Goodbye!")

if __name__ == "__main__":
    main()
