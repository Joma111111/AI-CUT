"""
数据库管理器
"""

import sqlite3
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger
import config

logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path or config.LOCAL_DB_PATH
        
        # 确保数据库目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        logger.info(f"数据库管理器初始化完成: {self.db_path}")
    
    def _init_database(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 项目表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                video_path TEXT,
                created_at TEXT,
                updated_at TEXT,
                version INTEGER,
                status TEXT,
                metadata TEXT
            )
        """)
        
        # 镜头表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenes (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                scene_index INTEGER,
                start_time REAL,
                end_time REAL,
                duration REAL,
                start_frame INTEGER,
                end_frame INTEGER,
                metadata TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # 关键帧表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keyframes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id TEXT,
                project_id TEXT,
                keyframe_index INTEGER,
                time REAL,
                frame_number INTEGER,
                image_path TEXT,
                image_hash TEXT,
                quality_score REAL,
                metadata TEXT,
                FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # 文案表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id TEXT,
                project_id TEXT,
                script TEXT,
                word_count INTEGER,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT,
                FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # 音频表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id TEXT,
                project_id TEXT,
                audio_path TEXT,
                duration REAL,
                voice TEXT,
                created_at TEXT,
                metadata TEXT,
                FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # 设置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("数据库表初始化完成")
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== 项目操作 ====================
    
    def save_project(self, project: Dict):
        """保存项目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO projects 
            (id, name, description, video_path, created_at, updated_at, version, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project['id'],
            project['name'],
            project.get('description', ''),
            project.get('video_path', ''),
            project.get('created_at', datetime.now().isoformat()),
            project.get('updated_at', datetime.now().isoformat()),
            project.get('version', 1),
            project.get('status', 'created'),
            json.dumps(project.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"项目已保存: {project['id']}")
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_project(self, project_id: str, updates: Dict):
        """更新项目"""
        updates['updated_at'] = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [project_id]
        
        cursor.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?",
            values
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"项目已更新: {project_id}")
    
    def delete_project(self, project_id: str):
        """删除项目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"项目已删除: {project_id}")
    
    # ==================== 镜头操作 ====================
    
    def save_project_scenes(self, project_id: str, scenes: List[Dict]):
        """保存项目的镜头列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 先删除旧数据
        cursor.execute("DELETE FROM scenes WHERE project_id = ?", (project_id,))
        
        # 插入新数据
        for scene in scenes:
            cursor.execute("""
                INSERT INTO scenes 
                (id, project_id, scene_index, start_time, end_time, duration, 
                 start_frame, end_frame, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scene['id'],
                project_id,
                scene['index'],
                scene['start_time'],
                scene['end_time'],
                scene['duration'],
                scene['start_frame'],
                scene['end_frame'],
                json.dumps(scene.get('metadata', {}))
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"镜头已保存: {len(scenes)} 个")
    
    def get_project_scenes(self, project_id: str) -> List[Dict]:
        """获取项目的镜头列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM scenes WHERE project_id = ? ORDER BY scene_index",
            (project_id,)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== 文案操作 ====================
    
    def save_project_scripts(self, project_id: str, scripts: List[Dict]):
        """保存项目的文案列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 先删除旧数据
        cursor.execute("DELETE FROM scripts WHERE project_id = ?", (project_id,))
        
        # 插入新数据
        for script in scripts:
            cursor.execute("""
                INSERT INTO scripts 
                (scene_id, project_id, script, word_count, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                script['scene_id'],
                project_id,
                script['script'],
                script.get('word_count', len(script['script'])),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(script.get('metadata', {}))
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"文案已保存: {len(scripts)} 个")
    
    def get_project_scripts(self, project_id: str) -> List[Dict]:
        """获取项目的文案列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM scripts WHERE project_id = ?",
            (project_id,)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== 设置操作 ====================
    
    def set_setting(self, key: str, value: str):
        """设置配置项"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """获取配置项"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row['value']
        return default
