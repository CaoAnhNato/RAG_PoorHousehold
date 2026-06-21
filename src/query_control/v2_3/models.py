from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ExtractionIssue(BaseModel):
    entity_type: str
    issue_type: str  # 'unresolved', 'ambiguous', 'missing'
    message: str
    value: Optional[str] = None
    candidates: Optional[List[str]] = None

class ExtractionReport(BaseModel):
    slots: Dict[str, Any] = Field(default_factory=dict)
    issues: List[ExtractionIssue] = Field(default_factory=list)
    
    def add_resolved(self, key: str, value: Any):
        """Thêm một thực thể đã được phân giải thành công."""
        self.slots[key] = value
        
    def add_issue(self, entity_type: str, issue_type: str, message: str, value: str = None, candidates: List[str] = None):
        """Thêm một vấn đề cần làm rõ (ambiguous, unresolved, missing)."""
        self.issues.append(ExtractionIssue(
            entity_type=entity_type,
            issue_type=issue_type,
            message=message,
            value=value,
            candidates=candidates
        ))
        
    @property
    def has_issues(self) -> bool:
        """Kiểm tra xem có vấn đề nào cần làm rõ không."""
        return len(self.issues) > 0
    
    def get_issues_by_type(self, issue_type: str) -> List[ExtractionIssue]:
        return [i for i in self.issues if i.issue_type == issue_type]
