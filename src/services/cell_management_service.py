import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class CellManagementService:
    """Manages notebook cells and their content"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def update_or_create_cell(
        self,
        notebook_id: UUID,
        cell_type: str,
        code: str,
        agent_id: str,
        position: int
    ) -> Dict[str, Any]:
        """Update existing cell or create new one"""
        
        try:
            # Check if cell already exists for this type
            existing_cell = await self._get_cell_by_type(notebook_id, cell_type)
            
            if existing_cell:
                # Update existing cell
                return await self._update_cell(
                    cell_id=existing_cell["id"],
                    code=code,
                    agent_id=agent_id
                )
            else:
                # Create new cell
                return await self._create_cell(
                    notebook_id=notebook_id,
                    cell_type=cell_type,
                    code=code,
                    agent_id=agent_id,
                    position=position
                )
                
        except Exception as e:
            logger.error(f"Error managing cell: {e}")
            raise
    
    async def _get_cell_by_type(self, notebook_id: UUID, cell_type: str) -> Optional[Dict[str, Any]]:
        """Get existing cell by type"""
        
        stmt = text("""
            SELECT id, code, version FROM notebook_cells 
            WHERE notebook_id = :notebook_id AND cell_type = :cell_type AND is_active = true
            ORDER BY version DESC LIMIT 1
        """)
        
        result = await self.db.execute(stmt, {
            "notebook_id": str(notebook_id),
            "cell_type": cell_type
        })
        
        row = result.fetchone()
        if row:
            return {
                "id": str(row.id),
                "code": row.code,
                "version": row.version
            }
        return None
    
    async def _create_cell(
        self,
        notebook_id: UUID,
        cell_type: str,
        code: str,
        agent_id: str,
        position: int
    ) -> Dict[str, Any]:
        """Create new cell"""
        
        cell_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        stmt = text("""
            INSERT INTO notebook_cells 
            (id, notebook_id, cell_type, code, agent_id, version, position, is_active, created_at, updated_at)
            VALUES (:id, :notebook_id, :cell_type, :code, :agent_id, :version, :position, :is_active, :created_at, :updated_at)
            RETURNING id
        """)
        
        result = await self.db.execute(stmt, {
            "id": cell_id,
            "notebook_id": str(notebook_id),
            "cell_type": cell_type,
            "code": code,
            "agent_id": agent_id,
            "version": 1,
            "position": position,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        })
        
        await self.db.commit()
        
        return {
            "cell_id": cell_id,
            "version": 1,
            "action": "created"
        }
    
    async def _update_cell(
        self,
        cell_id: str,
        code: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """Update existing cell with new version"""
        
        # Get current version
        current_version_stmt = text("""
            SELECT version FROM notebook_cells WHERE id = :cell_id
        """)
        
        version_result = await self.db.execute(current_version_stmt, {"cell_id": cell_id})
        current_version = version_result.scalar()
        new_version = current_version + 1
        
        # Update cell
        update_stmt = text("""
            UPDATE notebook_cells 
            SET code = :code, agent_id = :agent_id, version = :version, updated_at = :updated_at
            WHERE id = :cell_id
        """)
        
        await self.db.execute(update_stmt, {
            "cell_id": cell_id,
            "code": code,
            "agent_id": agent_id,
            "version": new_version,
            "updated_at": datetime.utcnow()
        })
        
        await self.db.commit()
        
        return {
            "cell_id": cell_id,
            "version": new_version,
            "action": "updated"
        }
    
    async def get_notebook_cells(self, notebook_id: UUID) -> List[Dict[str, Any]]:
        """Get all active cells for a notebook"""
        
        stmt = text("""
            SELECT id, cell_type, code, agent_id, version, position, created_at, updated_at
            FROM notebook_cells 
            WHERE notebook_id = :notebook_id AND is_active = true
            ORDER BY position, created_at
        """)
        
        result = await self.db.execute(stmt, {"notebook_id": str(notebook_id)})
        
        cells = []
        for row in result.fetchall():
            cells.append({
                "id": str(row.id),
                "cell_type": row.cell_type,
                "code": row.code,
                "agent_id": row.agent_id,
                "version": row.version,
                "position": row.position,
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat()
            })
        
        return cells
    
    async def get_complete_notebook_code(self, notebook_id: UUID) -> str:
        """Get all cells combined into complete code"""
        
        cells = await self.get_notebook_cells(notebook_id)
        
        if not cells:
            return "# No code generated yet"
        
        code_parts = []
        code_parts.append("# Complete DEAP Algorithm Generated by Multi-Agent System")
        code_parts.append("# " + "=" * 60)
        code_parts.append("")
        
        for cell in cells:
            code_parts.append(f"# {cell['cell_type'].upper()} - Generated by {cell['agent_id']}")
            code_parts.append("# " + "-" * 40)
            code_parts.append(cell['code'])
            code_parts.append("")
        
        return "\n".join(code_parts)