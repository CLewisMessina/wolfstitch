from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class SessionFile:
    path: str
    tag: Optional[str] = None
    config: Dict = field(default_factory=dict)
    chunks: List[str] = field(default_factory=list)

@dataclass
class Session:
    files: List[SessionFile] = field(default_factory=list)

    def add_file(self, path: str, config: Optional[Dict] = None, tag: Optional[str] = None):
        self.files.append(SessionFile(path=path, config=config or {}, tag=tag))

    def get_all_chunks(self) -> List[str]:
        return [chunk for f in self.files for chunk in f.chunks]

    def to_dict(self) -> Dict:
        return {
            "files": [
                {
                    "path": f.path,
                    "tag": f.tag,
                    "config": f.config,
                    "chunks": f.chunks
                } for f in self.files
            ]
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Session':
        session = Session()
        for file_data in data.get("files", []):
            session.files.append(SessionFile(
                path=file_data["path"],
                tag=file_data.get("tag"),
                config=file_data.get("config", {}),
                chunks=file_data.get("chunks", [])
            ))
        return session