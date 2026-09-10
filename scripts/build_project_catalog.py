from __future__ import annotations
import json
from pathlib import Path


def build(root: Path) -> list[dict]:
    projects=[]
    for path in sorted((root/'config'/'projects').glob('*.json')):
        data=json.loads(path.read_text(encoding='utf-8'))
        projects.append({
            'key': data['key'],
            'title': data['title'],
            'drive_folder_id': data['drive_folder_id'],
            'modules': data.get('modules', []),
        })
    return sorted(projects, key=lambda item: item['title'])


def main() -> None:
    root=Path(__file__).resolve().parents[1]
    target=root/'docs'/'project-catalog.json'
    target.write_text(json.dumps(build(root),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target)

if __name__=='__main__':
    main()
